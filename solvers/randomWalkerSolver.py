import json
import argparse
from collections import Counter
import numpy as np
from utils import convert_to_page_graph

# code inspired by: https://allendowney.github.io/DSIRP/pagerank.html#random-walk

class PageRankSolver():
    def __init__(self, json_file):
        self.pr_graph = convert_to_page_graph(json_file)
        self.page_rank_counter = Counter()

    def flip(self, prob):
        return np.random.random() < prob

    def solve(self, iter, damping):
        curr_node = np.random.choice(self.pr_graph)

        for _ in range(iter):
            if self.flip(damping):
                if len(curr_node.outward_nodes) == 0:
                    curr_node = np.random.choice(self.pr_graph)
                else:
                    curr_node = np.random.choice(curr_node.outward_nodes)
            else:
                curr_node = np.random.choice(self.pr_graph)

            self.page_rank_counter[curr_node.name] += 1

    def export(self, file_name):

        total = sum(self.page_rank_counter.values())
        for key in self.page_rank_counter:
            self.page_rank_counter[key] /= total

        return_dict = {}
        for node in self.pr_graph:
            return_dict[node.name] = self.page_rank_counter[node.name]

        with open(f"results/{file_name}", "w") as f:
            json.dump(return_dict, f, indent=4)


def parse():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Solve Graph with simple solver method")

    parser.add_argument("-i", "--iter", type=int,
                        default=1000, help="The amount of iterations")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--out_file_name", type=str,
                        default="result_walker.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:

        args = parse()

        solver = PageRankSolver(args.file_name)
        solver.solve(args.iter, 0.85)

        solver.export(args.out_file_name)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
