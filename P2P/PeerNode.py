import json
import argparse
from collections import Counter
import numpy as np
from utils import PageNode, convert_to_page_subgraph, load_subgraph_file
import zmq
from P2P import message_pb2
import logging
from collections import defaultdict

class PeerNode():
    def __init__(self, args, logger):
        self.document_graph, self.total_docs = convert_to_page_subgraph(
            args.file_name, args.subgraph)
        self.logger = logger
        self.port = args.port
        self.addr = args.addr
        self.subgraph = args.subgraph
        self.subgraph_info = load_subgraph_file(args.subgraph_file)
        self.damping = args.damping
        self.iterations = args.iterations
        self.epsilon = args.epsilon
        self.push = None
        self.pull = None

    def configure(self):
        self.logger.info("PeerNode::configure")
        context = zmq.Context()
        self.poller = zmq.Poller()

        self.logger.debug(
            "PeerNode::configure - obtain REP and REQ sockets")
        self.pull = context.socket(zmq.PULL)
        
        for subgraph_id in self.subgraph_info:
            if int(subgraph_id) != self.subgraph:
                self.logger.debug(f"PeerNode::configure - connecting PULL to {self.subgraph_info[subgraph_id]}")
                self.pull.connect("tcp://" + self.subgraph_info[subgraph_id])

        self.push = context.socket(zmq.PUSH)

        self.logger.debug(
            f"PeerNode::configure - bind the PUSH at {self.addr}:{self.port}")
        bind_string = "tcp://*:" + str(self.port)
        self.push.bind(bind_string)

        self.logger.info("PeerNode::configure completed")

    def driver(self):
        self.configure()
        self.calculate_pagerank()
        self.event_loop()

    def calculate_pagerank(self):
        self.logger.info("PeerNode::calculate_pagerank")

        outward_messages_to_send = defaultdict(list)
        
        for document, node in self.document_graph.items():
            page_rank_sum = 0
            for in_node in node.inward_nodes:
                out_degree = max(1, len(in_node.outward_nodes))
                page_rank_sum += (in_node.page_rank / out_degree)

            random_walk = (1 - self.damping) / self.total_docs
            new_page_rank = random_walk + self.damping * page_rank_sum
            rel_error = abs(node.page_rank - new_page_rank) / new_page_rank
            node.page_rank = new_page_rank

            for out_node in node.outward_nodes:
                if out_node.subgraph != self.subgraph and rel_error > self.epsilon:
                    outward_messages_to_send[out_node.subgraph].append((node.name, new_page_rank))

            self.update_page_graph(node.name, new_page_rank)

        for subgraph_index, new_pagerank_list in outward_messages_to_send.items():
            new_pagerank_id, new_pagerank_values = zip(*new_pagerank_list)
            new_pagerank_id = set(new_pagerank_id)
            new_pagerank_values = set(new_pagerank_values)

            self.logger.debug(f"Sending message to subgraph {subgraph_index} to update {new_pagerank_id} with {new_pagerank_values}")
            self.send_pagerank_message(new_pagerank_id, new_pagerank_values, subgraph_index)
            
    def send_pagerank_message(self, new_pagerank_id, new_pagerank_values, subgraph_id):
        self.logger.info("PeerNode::send_pagerank_message")

        new_pagerank_id = [str(x) for x in new_pagerank_id]
        new_pagerank_values = [str(x) for x in new_pagerank_values]

        update_req = message_pb2.updateReq()
        update_req.id_to_update[:] = new_pagerank_id
        update_req.pagerank_to_update[:] = new_pagerank_values
        update_req.subgraph_id = subgraph_id

        buf2send = update_req.SerializeToString()

        self.push.send(buf2send)

    def update_page_graph(self, node_to_update, new_page_rank):
        self.logger.debug(f"PeerNode::update_page_graph - updating {node_to_update}, and all its inward links, with {new_page_rank}")
        
        for document, node in self.document_graph.items():
            for in_node in node.inward_nodes:
                if in_node.name == node_to_update:
                    in_node.page_rank = new_page_rank

    def print_document_graph(self):
        for document, node in self.document_graph.items():
            self.logger.info(f"{document} has inward links to nodes {', '.join([in_node.name.split('_')[-1] for in_node in node.inward_nodes])}")
            self.logger.info(f"{document} has outward links to nodes {', '.join([out_node.name.split('_')[-1] for out_node in node.outward_nodes])}")
            
    def event_loop(self):
        try:
            self.logger.info("PeerNode::event_loop - run the event loop")
            iters = 0
            while True:
                self.logger.info("PeerNode::event_loop - run the event loop")
                bytes_rcvd = self.pull.recv()
                update_req = message_pb2.updateReq()
                update_req.ParseFromString(bytes_rcvd)
                if update_req.subgraph_id == self.subgraph:
                    self.handle_update(update_req)
                    iters += 1
                    if self.iterations == iters:
                        break

            self.logger.info("PeerNode::event_loop - out of the event loop")
        except Exception as e:
            raise e

    def handle_update(self, update_req):
        try:
            self.logger.info(f"PeerNode::handle_update")

            for node_id, new_rank in zip(update_req.id_to_update, [float(x) for x in update_req.pagerank_to_update]):
                self.update_page_graph(node_id, new_rank)

            self.calculate_pagerank()

        except Exception as e:
            raise e

def parse():
    parser = argparse.ArgumentParser(
        description="Start Mininet node")

    parser.add_argument("-s", "--subgraph", type=int,
                        default=1, help="What index subgraph is this?")

                        
    parser.add_argument("-it", "--iterations", type=int,
                        default=10, help="Number of pagerank iterations to run")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="File name input for graph of a peer")
    
    parser.add_argument("-sf", "--subgraph_file", type=str,
                        default="subgraph.json", help="Mapping of subgraph location to IP address")
    
    parser.add_argument("-e", "--epsilon", type=int,
                        default=0.0001, help="Some error threshold for the pagerank")
    
    parser.add_argument("-d", "--damping", type=float,
                        default=0.85, help="The damping factor or alpha for solver (ideally betweent 0.8 to 1.0)")

    parser.add_argument("-a", "--addr", default="localhost",
                        help="IP addr of this publisher to advertise (default: localhost)")

    parser.add_argument("-p", "--port", type=int, default=5577,
                        help="Port number on which our underlying ZMQ rep socket runs, default=5577")

    parser.add_argument("-l", "--loglevel", type=int, default=logging.DEBUG, choices=[
                        logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL], help="logging level, choices 10,20,30,40,50: default 20=logging.INFO")

    return parser.parse_args()


def main():
    try:
        args = parse()
        
        logging.info("Getting logger...")
        logger = logging.getLogger("PeerNode")
        logger.setLevel(args.loglevel)

        solver = PeerNode(args, logger)
        solver.driver()

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
