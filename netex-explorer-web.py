from graphviz import Digraph
import xml.etree.ElementTree as ET

class NeTExElement:
    def __init__(self, element):
        self.tag = element.tag
        self.attrib = element.attrib
        self.children = [NeTExElement(child) for child in element]
        self.references = self.extract_references()

    def __repr__(self):
        return f"{self.tag}: {self.attrib}"
    
    def extract_references(self):
        references = []
        for key, value in self.attrib.items():
            if 'ref' in key.lower():
                references.append(value)
        return references

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

def find_element_by_id(element, element_id):
    if element.attrib.get('id') == element_id:
        return element
    for child in element.children:
        result = find_element_by_id(child, element_id)
        if result:
            return result
    return None

def visualize_tree(element, graph=None, parent=None, depth=0, max_depth=4, start_tag=None, node_map=None):
    if graph is None:
        graph = Digraph()
        node_map = {}

    if start_tag:
        element = find_element_by_tag(element, start_tag)
        if not element:
            raise ValueError(f"Element with tag '{start_tag}' not found")

    if depth > max_depth:
        return graph
    
    # At certain node types we are going to cease the visualisation
    print(strip_namespace(element.tag))
    if strip_namespace(element.tag) in ['fareZones', 'scheduledStopPoints','cells','codespaces','FareTable','distanceMatrixElements']:
        return graph
    
    # At certain nodes with particular iD we are going to cease the visualisation
    if element.attrib.get('id') in ['fxc:UK:DFT:TypeOfFrame_UK_PI_METADATA_OFFER:FXCP:fxc',]:
        return graph

    element_id = element.attrib.get('id', str(id(element)))
    if element_id not in node_map:
        node_map[element_id] = f"node{len(node_map)}"
    
    node_id = node_map[element_id]
    clean_tag = strip_namespace(element.tag)
    formatted_attrib = format_attributes(element.attrib)
    graph.node(node_id, f"{clean_tag}\n{formatted_attrib}")
    

    if parent:
        edge_id = f"{parent}->{node_id}"
        graph.edge(parent, node_id, id=edge_id)

    for child in element.children:
        visualize_tree(child, graph, node_id, depth + 1, max_depth, node_map=node_map)


    # Add edges for references
    for ref in element.references:
        ref_element = find_element_by_id(element, ref)
        if ref_element:
            ref_node_id = node_map.get(ref_element.attrib.get('id', str(id(ref_element))), None)
            if ref_node_id:
                graph.edge(node_id, ref_node_id, style='dashed', color='blue')

    return graph

if __name__ == "__main__":
    netex_file = "./RBUS_X4_Outbound_BoostSingle.xml"
    netex_tree = parse_netex(netex_file)
    graph = visualize_tree(netex_tree, start_tag="dataObjects", max_depth=10)
    graph.attr(rankdir='LR')  # Set the orientation to Left to Right
    dot_data = graph.source

    with open("./graph.dot", "w") as f:
        f.write(dot_data)