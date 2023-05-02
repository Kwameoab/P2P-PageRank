import json
import argparse
import numpy as np
from utils import convert_to_page_graph, convert_to_matrix

# code inspired by: https://allendowney.github.io/DSIRP/pagerank.html#adjacency-matrix


class MatrixSolver():
    def __init__(self, json_file):
        self.graph_matrix = convert_to_matrix(json_file)
        self.pr_graph = convert_to_page_graph(json_file)
        self.ranks_array = None

    def solve(self, iter, alpha, walkers):
        nodes_len = len(self.graph_matrix)
        random_jumps = np.full((nodes_len, nodes_len), 1/nodes_len)
        google_graph_matrix = alpha * \
            self.graph_matrix + (1 - alpha) * random_jumps
        result_matrix = np.full(nodes_len, walkers)

        for i in range(iter):
            result_matrix = google_graph_matrix.T @ result_matrix

        self.ranks_array = result_matrix / result_matrix.sum()

    def export(self, file_name):
        return_dict = {}
        for index, node in enumerate(self.pr_graph):
            return_dict[node.name] = self.ranks_array[index]

        with open(f"results/{file_name}", "w") as f:
            json.dump(return_dict, f, indent=4)


def parse():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Solve Graph with simple solver method")

    parser.add_argument("-i", "--iter", type=int,
                        default=1000, help="The amount of iterations")

    parser.add_argument("-d", "--dampingFactor", type=float,
                        default=0.85, help="The damping factor or alpha for solver (ideally betweent 0.8 to 1.0)")

    parser.add_argument("-w", "--walkers", type=int,
                        default=100, help="The amount of walkers we per page when we start the simulation.")

    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="Input file for the graph")

    parser.add_argument("-of", "--out_file_name", type=str,
                        default="result_matrix.json", help="Output file after solving")

    return parser.parse_args()


def main():
    try:
        args = parse()

        solver = MatrixSolver(args.file_name)
        solver.solve(args.iter, args.dampingFactor, args.walkers)

        solver.export(args.out_file_name)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
