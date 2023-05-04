
import argparse
import json


def parse():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(description="Create Graph")

    parser.add_argument("-t", "--testing_file", type=str,
                        default="testing.sh", help="Output file for the testing")

    parser.add_argument("-r", "--results_folder", type=str,
                        default="P2P_results", help="Results folder")
    
    parser.add_argument("-f", "--file_name", type=str,
                        default="graph.json", help="File name input for graph of a peer")

    parser.add_argument("-sf", "--subgraph_file", type=str,
                        default="subgraph.json", help="Mapping of subgraph location to IP address")

    parser.add_argument("-s", "--subgraph", type=int,
                        default=5, help="Number of subgraphs to generate the script for")

    parser.add_argument("-p", "--port", type=int,
                        default=5577, help="Port to host the peer on")

    parser.add_argument("-it", "--iterations", type=int,
                        default=10, help="Number of pagerank iterations to run")

    parser.add_argument("-e", "--epsilon", type=float,
                        default=0.0001, help="Some error threshold for the pagerank")

    parser.add_argument("-d", "--damping", type=float,
                        default=0.85, help="The damping factor or alpha for solver (ideally betweent 0.8 to 1.0)")

    return parser.parse_args()


def main(args):
    subgraph_json = {}

    for i in range(1, args.subgraph + 1):
        subgraph_json[i] = f"10.0.0.{i}:{args.port}"

    with open(args.testing_file, "w") as f:
        for i in range(1, args.subgraph + 1):
            output_str = f"h{i} python3 -m P2P.PeerNode -s {i} -a 10.0.0.{i} -p {args.port} > P2P_results/node{i}.out -e {args.epsilon} -d {args.damping} -f {args.file_name} -it {args.iterations} 2>&1 & \n"
            f.write(output_str)

    with open(args.subgraph_file, "w") as f:
        json.dump(subgraph_json, f, indent=4)

    print(
        f"Done! Please make sure to run createGraph.py -s {args.subgraph} as well to generate the matching graph.")


if __name__ == "__main__":
    args = parse()
    main(args)
