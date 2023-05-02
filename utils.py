import json

class PageNode ():
    def __init__(self, name):
        self.name = name
        self.inward_nodes = []
        self.outward_nodes = []

def convert_to_page_graph(self, json_file):
    graph_list = []
    page_graph_list = []

    with open(json_file, "r") as f:
        graph_list = json.load(f)

    for node in graph_list:
        page_graph_list.append(PageNode(node["name"]))

    for index, node in enumerate(graph_list):
        for in_node in node["inwardLinks"]:
            in_index = int(str(in_node).split("_")[-1])
            page_graph_list[index].inward_nodes.append(page_graph_list[in_index])

        for out_node in node["outwardLinks"]:
            out_index = int(str(out_node).split("_")[-1])
            page_graph_list[index].outward_nodes.append(
                page_graph_list[out_index])

    return page_graph_list