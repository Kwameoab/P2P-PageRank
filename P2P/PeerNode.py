import json
import argparse
from collections import Counter
import numpy as np
from utils import PageNode, convert_to_page_subgraph
import zmq
import message_pb
import logging


class PeerNode():
    def __init__(self, args):
        self.document_graph = convert_to_page_subgraph(
            args.json_file, args.index)
        self.logger = logging.getLogger("PeerNode")
        self.port = args.port
        self.addr = args.addr
        self.rep = None
        self.req = None

    def configure(self):
        self.logger.info("PeerNode::configure")
        context = zmq.Context()
        self.poller = zmq.Poller()

        self.logger.debug(
            "PeerNode::configure - obtain REP and REQ sockets")
        self.req = context.socket(zmq.REQ)
        self.req = context.socket(zmq.REP)
        self.poller.register(self.rep, zmq.POLLIN)

        self.logger.debug(
            f"PeerNode::configure - bind the REP at {self.addr}:{self.port}")
        bind_string = "tcp://*:" + str(self.port)
        self.rep.bind(bind_string)

        self.logger.info("PeerNode::configure completed")

    def driver(self):
        self.configure()
        self.calculate_pagerank()
        self.event_loop()

    def calculate_pagerank(self):
        self.logger.info("PeerNode::calculate_pagerank")

    def send_pagerank_message(self):
        self.logger.info("PeerNode::send_pagerank_message")

    def update_page_graph(self):
        self.logger.info("PeerNode::update_page_graph")

    def event_loop(self, timeout=None):
        try:
            self.logger.info("PeerNode::event_loop - run the event loop")
            while self.handle_events:
                events = dict(self.poller.poll(timeout=timeout))

                if not events:
                    timeout = 0
                elif self.rep in events:
                    timeout = self.handle_update()
                elif self.req in events:
                    timeout = 0
                else:
                    raise Exception(f"Unknown event after poll: {events} ")

            self.logger.info("PeerNode::event_loop - out of the event loop")
        except Exception as e:
            raise e

    def handle_update(self):
        try:
            self.logger.info("PeerNode::handle_update")

            bytes_rcvd = self.rep.recv()
            self.logger.info(f"PeerNode::handle_update received {bytes_rcvd}")

            update_req = message_pb.updateReq()
            update_req.ParseFromString(bytes_rcvd)

            self.logger.info("PeerNode::handle_update - return response")

            is_ready_resp = message_pb.updateResp()
            buf2send = is_ready_resp.SerializeToString()
            self.logger.debug(
                "Stringified serialized buf = {}".format(buf2send))
            self.rep.send(is_ready_resp)

            self.update_page_graph(update_req)

            self.calculate_pagerank()

            return 0

        except Exception as e:
            raise e

def parse():
    parser = argparse.ArgumentParser(
        description="Start Mininet node")

    parser.add_argument("-i", "--index", type=int,
                        default=1, help="What index subgraph is this?")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="File name input for graph of a peer")

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

        solver = PeerNode(args)
        solver.driver()

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
