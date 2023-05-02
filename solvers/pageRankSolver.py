import argparse
import networkx as nx
import json


class PageRankSolver():
    def __init__(self, in_file, out_file):
        self.in_file = in_file
        self.out_file = f"results/{out_file}"

    def solve(self):
        graph_list = []
        nx_dict = {}

        with open(self.in_file, "r") as f:
            graph_list = json.load(f)

        for node in graph_list:
            outList = []
            for outNode in node["outward_links"]:
                outList.append(str(outNode))

            nx_dict[str(node["name"])] = outList

        nx_graph = nx.from_dict_of_lists(nx_dict, create_using=nx.DiGraph())

        with open(self.out_file, "w") as f:
            json.dump(nx.pagerank(nx_graph), f, indent=4)


def parse():
    parser = argparse.ArgumentParser(
        description="Solve Graph with NX method")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--out_file_name", type=str,
                        default="result_nx.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:
        args = parse()

        solver = PageRankSolver(args.file_name, args.out_file_name)
        solver.solve()

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
