# Author: Kwame Ampadu-Boateng
# Vanderbilt University
#
# Purpose:
#

import logging
import argparse
import random
import json
import random


class Node:
    def __init__(self, name):
        self.name = name
        self.in_nodes = []  # nodes that point inward towards me
        self.out_nodes = []  # ndoes I point outward to
        

class InternetGraph ():

    def __init__(self, logger):
        self.logger = logger
        self.node_list = []
        self.node_count = 0
        self.json_file = ""

    def configure(self, args):
        self.logger.debug("InternetGraph::configure")

        self.node_count = args.number
        self.json_file = args.file_name
        self.subgraph = args.subgraph

    def generate(self, in_deg, out_deg):
        for i in range(self.node_count):
            self.node_list.append(Node(f"Node_{i}"))

        in_weights = [0, 0]
        out_weights = [0, 0]
        for i in range(2, self.node_count):
            in_weights.append(1/(i**in_deg))
            out_weights.append(1/(i**out_deg))

        in_weights_sum = sum(in_weights)
        in_weights[0] = (1 - in_weights_sum) * 0.25
        in_weights[1] = 1 - sum(in_weights)
        self.logger.debug(
            f"This is in weight distribution total {sum(in_weights)} it should equal 1")

        out_weights_sum = sum(out_weights)
        out_weights[0] = (1 - out_weights_sum) * 0.25
        out_weights[1] = 1 - sum(out_weights)
        self.logger.debug(
            f"This is out weight distribution total {sum(out_weights)} it should equal 1")

        for i in range(self.node_count):
            in_count = random.choices(range(self.node_count), in_weights)[0]
            out_count = random.choices(range(self.node_count), out_weights)[0]

            self.in_connect(self.node_list[i], in_count)

            if len(self.node_list[i].out_nodes) < out_count:
                remainingout_count = out_count - len(self.node_list[i].out_nodes) 
                self.out_connect(self.node_list[i], remainingout_count)

        final_graph = []
        for node in self.node_list:
            in_list = []
            for in_node in node.in_nodes:
                in_list.append(in_node.name)

            out_list = []
            for out_node in node.out_nodes:
                out_list.append(out_node.name)

            entry = {
                "name": node.name,
                "inward_links": in_list,
                "outward_links": out_list,
                "subgraph": random.randint(1, self.subgraph)
            }
            
            final_graph.append(entry)


        with open(self.json_file, "w") as f:
            json.dump(final_graph, f, indent=4)

    def in_connect(self, node, in_count):
        for i in range(in_count):
            while True:
                node_to_connect = random.choice(self.node_list)
                if node_to_connect not in node.in_nodes and node_to_connect != node:
                    node.in_nodes.append(node_to_connect)
                    node_to_connect.out_nodes.append(node)
                    break

    def out_connect(self, node, out_count):
        for i in range(out_count):
            while True:
                node_to_connect = random.choice(self.node_list)
                if node_to_connect not in node.out_nodes and node_to_connect != node:
                    node.out_nodes.append(node_to_connect)
                    node_to_connect.in_nodes.append(node)
                    break


def parseCmdLineArgs():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(description="Create Graph")

    parser.add_argument("-n", "--number", type=int,
                        default=5000, help="Number of nodes in the graph")

    parser.add_argument("-in", "--in_deg", type=float,
                        default=2.1, help="In degree power for graph")

    parser.add_argument("-out", "--out_deg", type=float,
                        default=2.4, help="Out degree power for graph")

    parser.add_argument("-l", "--loglevel", type=int, default=logging.INFO, choices=[
                        logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL], help="logging level, choices 10,20,30,40,50: default 10=logging.DEBUG")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="Output file for the graph")
    
    parser.add_argument("-s", "--subgraph", type=int,
                        default=5, help="Number of subgraphs to randomly divide nodes into")

    return parser.parse_args()


def main():
    try:
        # obtain a system wide logger and initialize it to debug level to begin with
        logging.info(
            "Main - acquire a child logger and then log messages in the child")
        logger = logging.getLogger("InternetGraph")

        # first parse the arguments
        logger.debug("Main: parse command line arguments")
        args = parseCmdLineArgs()

        # reset the log level to as specified
        logger.debug("Main: resetting log level to {}".format(args.loglevel))
        logger.setLevel(args.loglevel)
        logger.debug("Main: effective log level is {}".format(
            logger.getEffectiveLevel()))

        # Obtain the test object
        logger.debug("Main: obtain the InternetGraph object")
        graph = InternetGraph(logger)

        # configure the object
        logger.debug("Main: configure the graph object")
        graph.configure(args)

        # now invoke the driver program
        logger.debug("Main: Create the graph")
        graph.generate(args.in_deg, args.out_deg)


    except Exception as e:
        logger.error("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    # set underlying default logging capabilities
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    main()
