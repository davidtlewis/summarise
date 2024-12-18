from graphviz import Digraph
import xml.etree.ElementTree as ET

# Global counter for generating unique node IDs
node_counter = 0

class NeTExElement:
    def __init__(self, element):
        global node_counter
        self.tag = element.tag
        self.attrib = element.attrib
        self.node_id = f"node{node_counter}"
        node_counter += 1
        self.children = [NeTExElement(child) for child in element]


    def __repr__(self):
        return f"{self.tag}: {self.attrib}"

def parse_netex(file_path):
    global node_counter
    node_counter = 0  # Reset the counter for each new file
    tree = ET.parse(file_path)
    root = tree.getroot()
    return NeTExElement(root)

def strip_namespace(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag

def format_attributes(attrib):
    return "\n".join([f"{key}: {value}" for key, value in attrib.items()])

def find_element_by_tag(element, tag):
    if strip_namespace(element.tag) == tag:
        return element
    for child in element.children:
        result = find_element_by_tag(child, tag)
        if result:
            return result
    return None

def visualize_tree(element, graph=None, parent=None, depth=0, max_depth=4, start_tag=None):
    if graph is None:
        graph = Digraph()

    if start_tag:
        element = find_element_by_tag(element, start_tag)
        if not element:
            raise ValueError(f"Element with tag '{start_tag}' not found")

    if depth > max_depth:
        return graph
    
    node_id = element.node_id
    clean_tag = strip_namespace(element.tag)
    formatted_attrib = format_attributes(element.attrib)
    graph.node(node_id, f"{clean_tag}\n{formatted_attrib}")

    if parent:
        edge_id = f"{parent}->{node_id}"
        graph.edge(parent, node_id, id=edge_id)

    for child in element.children:
        visualize_tree(child, graph, node_id, depth + 1, max_depth)

    return graph

if __name__ == "__main__":
    netex_file = "./RBUS_X4_Outbound_BoostSingle.xml"
    netex_tree = parse_netex(netex_file)
    graph = visualize_tree(netex_tree, start_tag="dataObjects", max_depth=4)
    graph.attr(rankdir='LR')  # Set the orientation to Left to Right
    dot_data = graph.source

    with open("./graph.dot", "w") as f:
        f.write(dot_data)