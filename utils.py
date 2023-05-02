import json
from collections import defaultdict

class PageNode ():
    def __init__(self, name):
        self.name = name
        self.inward_nodes = []
        self.outward_nodes = []
        self.page_rank = 1

def convert_to_page_graph(json_file):
    graph_list = []
    page_graph_list = []

    with open(json_file, "r") as f:
        graph_list = json.load(f)

    for node in graph_list:
        page_graph_list.append(PageNode(node["name"]))

    for index, node in enumerate(graph_list):
        for in_node in node["inward_links"]:
            in_index = int(str(in_node).split("_")[-1])
            page_graph_list[index].inward_nodes.append(page_graph_list[in_index])

        for out_node in node["outward_links"]:
            out_index = int(str(out_node).split("_")[-1])
            page_graph_list[index].outward_nodes.append(
                page_graph_list[out_index])

    return page_graph_list

def convert_to_page_subgraph(json_file, index):
    graph_list = []
    page_graph_list = defaultdict(PageNode)
    overall_graph = defaultdict(PageNode)

    with open(json_file, "r") as f:
        graph_list = json.load(f)

    for i, node in enumerate(graph_list):
        overall_graph[i] = PageNode(node["name"])
        if node["subgraph"] == index:
            page_graph_list[i] = PageNode(node["name"])

    for i, node in enumerate(graph_list):
        if node["subgraph"] == index:
            for in_node in node["inward_links"]:
                in_index = int(str(in_node).split("_")[-1])
                page_graph_list[i].inward_nodes.append(overall_graph[in_index])

            for out_node in node["outward_links"]:
                out_index = int(str(out_node).split("_")[-1])
                page_graph_list[i].outward_nodes.append(
                    overall_graph[out_index])

    return page_graph_list