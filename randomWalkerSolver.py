import json
import argparse
from collections import Counter
import numpy as np

# code inspired by: https://allendowney.github.io/DSIRP/pagerank.html#random-walk


class PageNode ():
    def __init__(self, name):
        self.name = name
        self.inwardNodes = []
        self.outwardNodes = []


class PageRankSolver ():
    def __init__(self, jsonFile):
        self.prGraph = self.convertToPageGraph(jsonFile)
        self.pageRankCounter = Counter()

    def convertToPageGraph(self, jsonFile):
        graphList = []
        pageGraphList = []

        with open(jsonFile, "r") as f:
            graphList = json.load(f)

        for node in graphList:
            pageGraphList.append(PageNode(node["name"]))

        for index, node in enumerate(graphList):
            for inNode in node["inwardLinks"]:
                inIndex = int(str(inNode).split("_")[-1])
                pageGraphList[index].inwardNodes.append(pageGraphList[inIndex])

            for outNode in node["outwardLinks"]:
                outIndex = int(str(outNode).split("_")[-1])
                pageGraphList[index].outwardNodes.append(
                    pageGraphList[outIndex])

        return pageGraphList

    def flip(self, prob):
        return np.random.random() < prob

    def solve(self, iter, damping):
        currPageNode = np.random.choice(self.prGraph)

        for _ in range(iter):
            if self.flip(damping):
                if len(currPageNode.outwardNodes) == 0:
                    currPageNode = np.random.choice(self.prGraph)
                else:
                    currPageNode = np.random.choice(currPageNode.outwardNodes)
            else:
                currPageNode = np.random.choice(self.prGraph)

            self.pageRankCounter[currPageNode.name] += 1

    def export(self, fileName):

        total = sum(self.pageRankCounter.values())
        for key in self.pageRankCounter:
            self.pageRankCounter[key] /= total

        returnDict = {}
        for node in self.prGraph:
            returnDict[node.name] = self.pageRankCounter[node.name]

        with open(f"results/{fileName}", "w") as f:
            json.dump(returnDict, f, indent=4)


def parseCmdLineArgs():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Solve Graph with simple solver method")

    parser.add_argument("-i", "--iter", type=int,
                        default=1000, help="The amount of iterations")

    parser.add_argument("-f", "--fileName", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--outFileName", type=str,
                        default="result_walker.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:

        args = parseCmdLineArgs()

        solver = PageRankSolver(args.fileName)
        solver.solve(args.iter, 0.85)

        solver.export(args.outFileName)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
