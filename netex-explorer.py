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
        # graph.attr(size='20,20')  # Increase the size of the output image

    if start_tag:
        element = find_element_by_tag(element, start_tag)
        if not element:
            raise ValueError(f"Element with tag '{start_tag}' not found")
        

    if depth > max_depth or element.tag.endswith("Element") or element.tag in ["Cell", "scheduledStopPoint","DistanceMatrixElement","PriceGroup","PriceGroupElement","PriceGroupElementPrice","PriceGroupElementRef","PriceGroupRef","PriceGroupRefPrice","PriceGroupRefStructure","PriceGroupRefStructureElement","PriceGroupRefStructureElementPrice","PriceGroupRefStructureElementRef","PriceGroupRefStructureRef","PriceGroupRefStructureRefPrice","PriceGroupRefStructureRefStructure","PriceGroupRefStructureRefStructureElement","PriceGroupRefStructureRefStructureElementPrice","PriceGroupRefStructureRefStructureElementRef","PriceGroupRefStructureRefStructureRef","PriceGroupRefStructureRefStructureRefPrice","PriceGroupRefStructureRefStructureRefStructure","PriceGroupRefStructureRefStructureRefStructureElement","PriceGroupRefStructureRefStructureRefStructureElementPrice","PriceGroupRefStructureRefStructureRefStructureElementRef","PriceGroupRefStructureRefStructureRefStructureRef","PriceGroupRefStructureRefStructureRefStructureRefPrice","PriceGroupRefStructureRefStructureRefStructureRefStructure","PriceGroupRefStructureRefStructureRefStructureRefStructureElement","PriceGroupRefStructureRefStructureRefStructureRefStructureElementPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureElementRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRefPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructure","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElement","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElementPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElementRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRefPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRefStructure","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElement","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElementPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElementRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRefPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRefStructure","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElement","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElementPrice","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureElementRef","PriceGroupRefStructureRefStructureRefStructureRefStructureRefStructureRef","fareTables" ,"GeographicalUnit"]:
        return graph
    
    node_id = str(id(element))
    clean_tag = strip_namespace(element.tag)
    formatted_attrib = format_attributes(element.attrib)
    graph.node(node_id, f"{clean_tag}\n{formatted_attrib}")

    if parent:
        graph.edge(parent, node_id)

    for child in element.children:
        visualize_tree(child, graph, node_id, depth=depth+1, max_depth=max_depth)

    return graph

if __name__ == "__main__":
    netex_file = "./RBUS_X4_Outbound_BoostSingle.xml"
    netex_tree = parse_netex(netex_file)
    graph = visualize_tree(netex_tree, start_tag="dataObjects", max_depth=4)
    # graph.render("netex_tree", format="png", view=True)
    graph.attr(rankdir='LR')  # Set the orientation to Top to Bottom
    graph.render("output_graph", format="png")