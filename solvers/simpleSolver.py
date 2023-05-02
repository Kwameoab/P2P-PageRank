import json
import argparse
from utils import convert_to_page_graph
# code inspired by: https://github.com/chonyy/page_rank-HITS-SimRank/tree/675414a5c74d804a77869723f964f2aa3b58a53b


class PageRankSolver ():
    def __init__(self, json_file):
        self.pr_graph = convert_to_page_graph(json_file)

    def solve(self, iter, alpha):
        for i in range(iter):
            self.one_iteration(alpha)
            self.normalize_page_rank()

    def one_iteration(self, damping):
        for node in self.pr_graph:
            self.update(node, node.inward_nodes,
                                damping, len(self.pr_graph))

    def update(self, node, inward_nodes, damping, total_nodes):
        page_rank_sum = 0
        for in_node in inward_nodes:
            out_degree = max(1, len(in_node.outward_nodes))
            page_rank_sum += (in_node.page_rank / out_degree)

        random_walk = (1 - damping) / total_nodes
        node.page_rank = random_walk + damping * page_rank_sum

    def normalize_page_rank(self):
        page_rank_sum = 0

        for node in self.pr_graph:
            page_rank_sum += node.page_rank

        for node in self.pr_graph:
            node.page_rank = node.page_rank / page_rank_sum

    def export(self, file_name):
        total = 0
        json_dict = {}

        for node in self.pr_graph:
            total += node.page_rank

        for node in self.pr_graph:
            json_dict[node.name] = node.page_rank / total

        with open(f"results/{file_name}", "w") as f:
            json.dump(json_dict, f, indent=4)


def parse():
    parser = argparse.ArgumentParser(
        description="Solve Graph with simple solver method")

    parser.add_argument("-i", "--iter", type=int,
                        default=1000, help="The amount of iterations")
    
    parser.add_argument("-d", "--dampingFactor", type=float,
                        default=0.85, help="The damping factor or alpha for solver (ideally betweent 0.8 to 1.0)")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--out_file_name", type=str,
                        default="result_simple.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:
        args = parse()

        solver = PageRankSolver(args.file_name)
        solver.solve(args.iter, args.dampingFactor)

        solver.export(args.out_file_name)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
