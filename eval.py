import json
import argparse
import numpy as np
from utils import convert_page_ranking_to_dict


class Evaluator():
    def __init__(self, correct_file, input_file):
        self.correct_answer = convert_page_ranking_to_dict(correct_file)
        self.input_answer = convert_page_ranking_to_dict(input_file)
        self.results = {}

    def evaluate(self):
        for name in self.correct_answer:
            self.results[name] = abs(
                self.correct_answer[name] - self.input_answer[name]) / self.correct_answer[name]

        average_error = sum(self.results.values()) / len(self.results)
        self.results["average_error"] = average_error

    def export(self, file_name):
        with open(file_name, "w") as f:
            json.dump(self.results, f, indent=4)


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

    return parser.parse_args()


def main():
    try:
        args = parse()

        evaluator = Evaluator(args.correct_file_name, args.input_file_name)
        evaluator.evaluate()

        evaluator.export(args.output_file_name)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return


if __name__ == "__main__":

    main()
