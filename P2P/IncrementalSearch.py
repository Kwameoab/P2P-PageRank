import json
import argparse
from collections import Counter
import numpy as np
from utils import PageNode, convert_to_page_subgraph, load_subgraph_file
import zmq
from P2P import message_pb2
import logging
from collections import defaultdict
import random

class IncrementalSearch():
    def __init__(self, args, logger):
        self.document_graph, self.total_docs = convert_to_page_subgraph(
            args.file_name, args.subgraph)
        self.logger = logger
        self.port = args.port
        self.addr = args.addr
        self.subgraph = args.subgraph
        self.subgraph_info = load_subgraph_file(args.subgraph_file)
        self.folder = args.folder
        self.push = None
        self.pull = None

    def configure(self):
        self.logger.info("PeerNode_ks::configure")
        context = zmq.Context()
        self.poller = zmq.Poller()

        self.logger.debug(
            "PeerNode_ks::configure - obtain REP and REQ sockets")
        self.pull = context.socket(zmq.PULL)
        
        for subgraph_id in self.subgraph_info:
            if int(subgraph_id) != self.subgraph:
                self.logger.debug(f"PeerNode_ks::configure - connecting PULL to {self.subgraph_info[subgraph_id]}")
                self.pull.connect("tcp://" + self.subgraph_info[subgraph_id])

        self.push = context.socket(zmq.PUSH)

        self.logger.debug(
            f"PeerNode_ks::configure - bind the PUSH at {self.addr}:{self.port}")
        bind_string = "tcp://*:" + str(self.port)
        self.push.bind(bind_string)

        self.logger.info("PeerNode_ks::configure completed")

    def driver(self, args):
        self.configure()
        # self.calculate_pagerank()
        queries = self.generate_query(args)

        for query in queries:
            for word in query:
                self.incremental_search(args.percent, word)

    def generate_query(self, args):
        queries = []
        with open(args.doc_details) as f:
            doc_details = json.load(f)
            top_100_words = doc_details['top_100']

            for i in range(args.num_queries):
                query = random.sample(top_100_words, k=args.query_size)
                queries.append(query)

        return queries

    def incremental_search(self, args, word):
        docs = self.get_documents(word)
        top_docs = docs[:args.percent*0.1]

        return top_docs

    def get_documents(self, word):
        # get the word index for term in search query 
        word_index = 0
        with open("../corpus/word_to_index") as f:
            word_index = json.load(f)[word]

        # is the peer responsible for this word index?
        for i in range(50):
            json_file = f"{i}.json"

            node_ids = []
            with open(f"../P2P_ks_results/{json_file}") as jf:
                peer_file = json.load(jf)
                node_ids = peer_file.keys()

            doc_ids = []
            with open("../graph_ks_docs.json") as gk:
                node_to_doc = json.load(gk)
                for node in node_to_doc:
                    doc_ids.append(node['doc'])

            if word_index in doc_ids:
                with open("../index_to_doc.json") as itd:
                    return json.load(itd)[str(word_index)]

        return []

    def send_document_hits(self, documents):
        document_req = message_pb2.docReq()
        document_req.documents[:] = documents

        buf2send = document_req.SerializeToString()
        try:
            self.push.send(buf2send)
        except zmq.ZMQError as e:
            self.logger.info(e)

    # def event_loop(self):
    #     try:
    #         self.logger.info("PeerNode_ks::event_loop - run the event loop")
    #         iters = 0
    #         while True:
    #             self.logger.info("PeerNode_ks::event_loop - run the event loop")
    #             try:
    #                 bytes_rcvd = self.pull.recv(flags=zmq.NOBLOCK)
    #                 document_req = message_pb2.docReq()
    #                 document_req.ParseFromString(bytes_rcvd)
    #                 if self.iterations == iters:
    #                     break
    #                 iters += 1
    #             except zmq.ZMQError as e:
    #                 if e.errno == zmq.EAGAIN:
    #                     self.logger.info("No message yet.")

    #         self.logger.info("PeerNode_ks::event_loop - out of the event loop")
    #     except Exception as e:
    #         raise e

    # def handle_update(self, update_req):
    #     try:
    #         self.logger.info(f"PeerNode_ks::handle_update")

    #         for node_id, new_rank in zip(update_req.id_to_update, [float(x) for x in update_req.pagerank_to_update]):
    #             self.update_page_graph(node_id, new_rank)

    #         self.calculate_pagerank()

    #     except Exception as e:
    #         raise e
        
    # def output(self):
    #     self.logger.info("PeerNode_ks::output")
    #     result = {}

    #     for value in self.document_graph.values():
    #         result[value.name] = value.page_rank


    #     with open(f"{self.folder}/{self.subgraph}.json", "w") as f:
    #         json.dump(result, f, indent=4)

def parse():
    parser = argparse.ArgumentParser(
        description="Start Mininet node")

    parser.add_argument("-s", "--subgraph", type=int,
                        default=1, help="What index subgraph is this?")

    parser.add_argument("-fo", "--folder", type=str,
                        default="P2P_ks_results", help="Folder output")

    parser.add_argument("-dd", "--doc_details", type=str,
                        default="corpus/document_details.json", help="Contains top 100 most common words from documents")
    
    parser.add_argument("-n", "--num_queries", type=int,
                        default="20", help="Number of search queries that we want to generate")

    parser.add_argument("-qs", "--query_size", type=int,
                        default="2", help="Length of search query that we want to generate")

    parser.add_argument("-pct", "--percent", type=int,
                        default="10", help="Percent of hits transferred to next peer")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="File name input for graph of a peer")
    
    parser.add_argument("-sf", "--subgraph_file", type=str,
                        default="subgraph.json", help="Mapping of subgraph location to IP address")
    
    parser.add_argument("-a", "--addr", default="localhost",
                        help="IP addr of this publisher to advertise (default: localhost)")

    parser.add_argument("-p", "--port", type=int, default=5577,
                        help="Port number on which our underlying ZMQ rep socket runs, default=5577")

    parser.add_argument("-l", "--loglevel", type=int, default=logging.INFO, choices=[
                        logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL], help="logging level, choices 10,20,30,40,50: default 20=logging.INFO")

    return parser.parse_args()


def main():
    try:
        args = parse()
        
        logging.info("Getting logger...")
        logger = logging.getLogger("PeerNode")
        logger.setLevel(args.loglevel)

        solver = IncrementalSearch(args, logger)
        solver.driver(args)
        # solver.output()

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
