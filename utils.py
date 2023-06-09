import json
from collections import defaultdict
import networkx as nx
import os

class PageNode ():
    def __init__(self, name, subgraph):
        self.name = name
        self.inward_nodes = []
        self.outward_nodes = []
        self.page_rank = 1
        self.subgraph = subgraph

def convert_to_matrix(json_file):
    graph_list = []
    nx_dict = {}

    with open(json_file, "r") as f:
        graph_list = json.load(f)

    for node in graph_list:
        outList = []
        for outNode in node["outward_links"]:
            outList.append(str(outNode))

        nx_dict[str(node["name"])] = outList

    nx_graph = nx.from_dict_of_lists(nx_dict, create_using=nx.DiGraph())
    graphMatrix = nx.to_numpy_array(nx_graph)

    for r_index, row in enumerate(graphMatrix):
        outSum = sum(row)
        if outSum == 0:
            outSum = 1

        for c_index, col in enumerate(row):
            graphMatrix[r_index][c_index] = graphMatrix[r_index][c_index] / outSum

    return graphMatrix


def convert_to_page_graph(json_file):
    graph_list = []
    page_graph_list = []

    with open(json_file, "r") as f:
        graph_list = json.load(f)

    for node in graph_list:
        page_graph_list.append(PageNode(node["name"], node["subgraph"]))

    for index, node in enumerate(graph_list):
        for in_node in node["inward_links"]:
            in_index = int(str(in_node).split("_")[-1])
            page_graph_list[index].inward_nodes.append(
                page_graph_list[in_index])

        for out_node in node["outward_links"]:
            out_index = int(str(out_node).split("_")[-1])
            page_graph_list[index].outward_nodes.append(
                page_graph_list[out_index])

    return page_graph_list

def load_subgraph_file(json_file):
    with open(json_file, "r") as f:
        subgraph_list = json.load(f)
    return subgraph_list

def convert_to_page_subgraph(json_file, index):
    graph_list = []
    page_graph_list = []

    with open(json_file, "r") as f:
        graph_list = json.load(f)

    for node in graph_list:
        page_graph_list.append(PageNode(node["name"], node["subgraph"]))

    for index, node in enumerate(graph_list):
        for in_node in node["inward_links"]:
            in_index = int(str(in_node).split("_")[-1])
            page_graph_list[index].inward_nodes.append(
                page_graph_list[in_index])

        for out_node in node["outward_links"]:
            out_index = int(str(out_node).split("_")[-1])
            page_graph_list[index].outward_nodes.append(
                page_graph_list[out_index])

    return page_graph_list, len(graph_list)

def convert_page_ranking_to_dict(json_file):
    with open(json_file, "r") as f:
        return json.load(f)

def convert_results_ranking_to_dict(results_folder):
    results = {}
    for file in os.listdir(results_folder):
        if "json" in file:
            with open(f"{results_folder}/{file}", "r") as f:
                results.update(json.load(f))

    return results