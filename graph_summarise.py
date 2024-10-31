import xml.etree.ElementTree as ET
import argparse
import networkx as nx
import matplotlib.pyplot as plt

def parse_netex_fares(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the Netex namespace
    ns = {'netex': 'http://www.netex.org.uk/netex'}

    # Initialize data structures to hold information
    tariffs = []
    fare_structure_elements = []

    # Extracting tariffs and their types
    for tariff in root.findall('.//netex:Tariff', ns):
        tariff_id = tariff.get('id')
        tariff_name = tariff.find('.//netex:Name', ns).text if tariff.find('.//netex:Name', ns) is not None else None
        fare_type = tariff.find('.//netex:TypeOfTariffRef', ns).get('ref') if tariff.find('.//netex:TypeOfTariffRef', ns) is not None else None

        tariffs.append({
            'tariff_id': tariff_id,
            'tariff_name': tariff_name,
            'fare_type': fare_type
        })

    # Extracting fare structure elements
    for fare_element in root.findall('.//netex:FareStructureElement', ns):
        element_id = fare_element.get('id')
        element_name = fare_element.find('.//netex:Name', ns).text if fare_element.find('.//netex:Name', ns) is not None else None
        fare_structure_type = fare_element.find('.//netex:TypeOfFareStructureElementRef', ns).get('ref') if fare_element.find('.//netex:TypeOfFareStructureElementRef', ns) is not None else None

        # Extracting distance matrix elements within each fare structure element
        distance_matrix_elements = []
        for distance_matrix in fare_element.findall('.//netex:DistanceMatrixElement', ns):
            start_zone = distance_matrix.find('.//netex:StartTariffZoneRef', ns).get('ref') if distance_matrix.find('.//netex:StartTariffZoneRef', ns) is not None else None
            end_zone = distance_matrix.find('.//netex:EndTariffZoneRef', ns).get('ref') if distance_matrix.find('.//netex:EndTariffZoneRef', ns) is not None else None

            # Extracting price group references if available
            price_groups = [pg.get('ref') for pg in distance_matrix.findall('.//netex:PriceGroupRef', ns)]
            distance_matrix_elements.append({
                'start_zone': start_zone,
                'end_zone': end_zone,
                'price_groups': price_groups
            })

        fare_structure_elements.append({
            'element_id': element_id,
            'element_name': element_name,
            'fare_structure_type': fare_structure_type,
            'distance_matrix_elements': distance_matrix_elements
        })

    return tariffs, fare_structure_elements

def create_graph(tariffs, fare_structure_elements):
    # Initialize a directed graph
    G = nx.DiGraph()

    # Add tariffs as nodes
    for tariff in tariffs:
        tariff_label = f"Tariff: {tariff['tariff_name']} ({tariff['fare_type']})"
        G.add_node(tariff['tariff_id'], label=tariff_label, color='skyblue', type='tariff')

    # Add fare structure elements and their connections
    for element in fare_structure_elements:
        element_label = f"FareStructureElement: {element['element_name']} ({element['fare_structure_type']})"
        G.add_node(element['element_id'], label=element_label, color='lightgreen', type='fare_structure')

        # Link DistanceMatrixElements
        for matrix in element['distance_matrix_elements']:
            start_zone = matrix['start_zone']
            end_zone = matrix['end_zone']
            if start_zone and end_zone:
                # Add zones as nodes
                if start_zone not in G:
                    G.add_node(start_zone, label=f"Zone: {start_zone}", color='orange', type='zone')
                if end_zone not in G:
                    G.add_node(end_zone, label=f"Zone: {end_zone}", color='orange', type='zone')

                # Connect start zone to end zone
                G.add_edge(start_zone, end_zone, label=f"Price Groups: {', '.join(matrix['price_groups'])}")

    return G

def visualize_graph(G):
    # Get node colors and labels
    colors = [G.nodes[node].get('color', 'gray') for node in G]
    labels = nx.get_node_attributes(G, 'label')

    # Draw the graph
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, seed=42)  # Positioning for readability
    nx.draw(G, pos, node_color=colors, with_labels=True, labels=labels, node_size=2000, font_size=8, font_weight='bold', edge_color='gray', arrows=True)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, label_pos=0.5)
# %%
    plt.title("Netex Fares Model Visualization")
    plt.show()

if __name__ == "__main__":
    # Set up argument parser
    # parser = argparse.ArgumentParser(description="Parse a Netex fares XML file and visualize fare model relationships.")
    # parser.add_argument('file_path', help="Path to the Netex fares XML file")

    # Parse command-line arguments
    # args = parser.parse_args()
    
    # Parse the Netex fares file
    tariffs, fare_structure_elements = parse_netex_fares("../xml/line8415.xml")
    # tariffs, fare_structure_elements = parse_netex_fares(args.file_path)
    # Create graph
    G = create_graph(tariffs, fare_structure_elements)

    # Visualize the graph
    visualize_graph(G)

