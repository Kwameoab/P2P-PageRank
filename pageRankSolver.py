import argparse
import networkx as nx
import json


class PageRankSolver ():
    def __init__(self, inFile, outFile):
        self.inFile = inFile
        self.outFile = f"results/{outFile}"

    def solve(self):
        graphList = []
        nxDict = {}

        with open(self.inFile, "r") as f:
            graphList = json.load(f)

        for node in graphList:
            outList = []
            for outNode in node["outwardLinks"]:
                outList.append(str(outNode))

            nxDict[str(node["name"])] = outList

        nxGraph = nx.from_dict_of_lists(nxDict, create_using=nx.DiGraph())

        with open(self.outFile, "w") as f:
            json.dump(nx.pagerank(nxGraph), f, indent=4)


def parseCmdLineArgs():
    parser = argparse.ArgumentParser(
        description="Solve Graph with NX method")

    parser.add_argument("-f", "--fileName", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--outFileName", type=str,
                        default="result_nx.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:
        args = parseCmdLineArgs()

        solver = PageRankSolver(args.fileName, args.outFileName)
        solver.solve()

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
