import json
import argparse
import numpy as np
from utils import convert_page_ranking_to_dict, convert_results_ranking_to_dict


class Evaluator():
    def __init__(self, args):
        self.correct_answer = convert_page_ranking_to_dict(args.correct_file_name)
        self.output_file_name = args.output_file_name
        if args.p2p:
            self.input_answer = convert_results_ranking_to_dict(args.result_folder)
            self.export("eval/p2p_results.json", self.input_answer)
        else:
            self.input_answer = convert_page_ranking_to_dict(args.input_file_name)
            
        self.results = {}

    def evaluate(self):
        for name in self.correct_answer:
            self.results[name] = abs(
                self.correct_answer[name] - self.input_answer[name]) / self.correct_answer[name]

        average_error = sum(self.results.values()) / len(self.results)
        self.results["average_error"] = average_error
        self.export(self.output_file_name, self.results)

    def export(self, file_name, output):
        with open(file_name, "w") as f:
            json.dump(output, f, indent=4)


def parse():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Evalute 2 ranks to evaluite how close the input rank is to correct rank.")

    parser.add_argument("-cf", "--correct_file_name", type=str,
                        default="results/result_matrix.json", help="Input file for the correct ranking")

    parser.add_argument("-if", "--input_file_name", type=str,
                        default="results/result_simple.json", help="Input file for the input ranking")

    parser.add_argument("-o", "--output_file_name", type=str,
                        default="eval/eval_simple.json", help="Output file after comparison")
    
    parser.add_argument("-r", "--result_folder", type=str,
                        default="P2P_results", help="P2P results folder")
    
    parser.add_argument("-p2p", "--p2p", action="store_true", help="Whether to use P2P results")

    return parser.parse_args()


def main():
    try:
        args = parse()

        evaluator = Evaluator(args)
        evaluator.evaluate()

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
