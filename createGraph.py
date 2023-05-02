# Author: Kwame Ampadu-Boateng
# Vanderbilt University
#
# Purpose:
#

import logging
import argparse
import random
import json


class Node:
    def __init__(self, name):
        self.name = name
        self.inNodes = []  # nodes that point inward towards me
        self.outNodes = []  # ndoes I point outward to
        

class InternetGraph ():

    def __init__(self, logger):
        self.logger = logger
        self.nodeList = []
        self.nodeCount = 0
        self.jsonFile = ""

    def configure(self, args):
        self.logger.debug("InternetGraph::configure")

        self.nodeCount = args.number
        self.jsonFile = args.fileName

    def generate(self):
        for i in range(self.nodeCount):
            self.nodeList.append(Node(f"Node_{i}"))

        inWeights = [0, 0]
        outWeights = [0, 0]
        for i in range(2, self.nodeCount):
            inWeights.append(1/(i**2.1))
            outWeights.append(1/(i**2.4))

        inWeightsSum = sum(inWeights)
        inWeights[0] = (1 - inWeightsSum) * 0.25
        inWeights[1] = 1 - sum(inWeights)
        self.logger.debug(
            f"This is in weight distribution total {sum(inWeights)} it should equal 1")

        outWeightsSum = sum(outWeights)
        outWeights[0] = (1 - outWeightsSum) * 0.25
        # outWeights[1] = (1 - outWeightsSum) * 0.75
        outWeights[1] = 1 - sum(outWeights)
        self.logger.debug(
            f"This is out weight distribution total {sum(outWeights)} it should equal 1")

        for i in range(self.nodeCount):
            inCount = random.choices(range(self.nodeCount), inWeights)[0]
            outCount = random.choices(range(self.nodeCount), outWeights)[0]

            self.in_connect(self.nodeList[i], inCount)

            if len(self.nodeList[i].outNodes) < outCount:
                remainingOutCount = outCount - len(self.nodeList[i].outNodes) 
                self.out_connect(self.nodeList[i], remainingOutCount)

        finalGraph = []
        for node in self.nodeList:
            inwardList = []
            for inNode in node.inNodes:
                inwardList.append(inNode.name)

            outwardList = []
            for outNode in node.outNodes:
                outwardList.append(outNode.name)

            entry = {
                "name": node.name,
                "inwardLinks": inwardList,
                "outwardLinks": outwardList
            }
            finalGraph.append(entry)

        with open(self.jsonFile, "w") as f:
            json.dump(finalGraph, f, indent=4)

    def in_connect(self, node, inCount):
        for i in range(inCount):
            while True:
                nodeToConnect = random.choice(self.nodeList)
                if nodeToConnect not in node.inNodes and nodeToConnect != node:
                    node.inNodes.append(nodeToConnect)
                    nodeToConnect.outNodes.append(node)
                    break

    def out_connect(self, node, outCount):
        for i in range(outCount):
            while True:
                nodeToConnect = random.choice(self.nodeList)
                if nodeToConnect not in node.outNodes and nodeToConnect != node:
                    node.outNodes.append(nodeToConnect)
                    nodeToConnect.inNodes.append(node)
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

    parser.add_argument("-f", "--fileName", type=str,
                        default="graph.json", help="Output file for the graph")

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
        graph.generate()

    except Exception as e:
        logger.error("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    # set underlying default logging capabilities
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    main()
