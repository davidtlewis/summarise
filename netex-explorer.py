import lxml.etree as ET
from graphviz import Digraph

class NeTExElement:
    def __init__(self, element):
        self.tag = element.tag
        self.attrib = element.attrib
        self.children = [NeTExElement(child) for child in element]

    def __repr__(self):
        return f"{self.tag}: {self.attrib}"

def parse_netex(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return NeTExElement(root)

def visualize_tree(element, graph=None, parent=None):
    if graph is None:
        graph = Digraph()

    node_id = str(id(element))
    graph.node(node_id, f"{element.tag}\n{element.attrib}")

    if parent:
        graph.edge(parent, node_id)

    for child in element.children:
        visualize_tree(child, graph, node_id)

    return graph

if __name__ == "__main__":
    netex_file = "./RBUS_X4_Outbound_BoostSingle.xml"
    netex_tree = parse_netex(netex_file)
    graph = visualize_tree(netex_tree)
    graph.render("netex_tree", format="png", view=True)