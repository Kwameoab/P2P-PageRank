import json
import argparse

# code inspired by: https://github.com/chonyy/PageRank-HITS-SimRank/tree/675414a5c74d804a77869723f964f2aa3b58a53b


class PageNode ():
    def __init__(self, name):
        self.name = name
        self.inwardNodes = []
        self.outwardNodes = []
        self.pageRank = 1


class PageRankSolver ():
    def __init__(self, jsonFile):
        self.prGraph = self.convertToPageGraph(jsonFile)

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

    def solve(self, iter):
        for i in range(iter):
            self.oneIteration(0.85)
            self.normalizePageRank()

    def oneIteration(self, damping):
        for node in self.prGraph:
            self.updatePageRank(node, node.inwardNodes,
                                damping, len(self.prGraph))

    def updatePageRank(self, node, inwardNodes, damping, totalNodes):
        pageRankSum = 0
        for inNode in inwardNodes:
            outDeg = max(1, len(inNode.outwardNodes))
            pageRankSum += (inNode.pageRank / outDeg)

        randomWalk = (1 - damping) / totalNodes
        node.pageRank = randomWalk + damping * pageRankSum

    def normalizePageRank(self):
        pageRankSum = 0

        for node in self.prGraph:
            pageRankSum += node.pageRank

        for node in self.prGraph:
            node.pageRank = node.pageRank / pageRankSum

    def export(self, fileName):
        sumTotal = 0
        exportJson = {}

        for node in self.prGraph:
            sumTotal += node.pageRank

        for node in self.prGraph:
            exportJson[node.name] = node.pageRank / sumTotal

        with open(f"results/{fileName}", "w") as f:
            json.dump(exportJson, f, indent=4)


def parseCmdLineArgs():
    parser = argparse.ArgumentParser(
        description="Solve Graph with simple solver method")

    parser.add_argument("-i", "--iter", type=int,
                        default=1000, help="The amount of iterations")

    parser.add_argument("-f", "--fileName", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--outFileName", type=str,
                        default="result_simple.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:
        args = parseCmdLineArgs()

        solver = PageRankSolver(args.fileName)
        solver.solve(args.iter)

        solver.export(args.outFileName)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
