import xml.etree.ElementTree as ET
import argparse

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
            price_groups = []
            for price_group in distance_matrix.findall('.//netex:PriceGroupRef', ns):
                price_groups.append(price_group.get('ref'))

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

    usertype = (root.find('.//netex:UserType', ns)).text
    producttype = (root.find('.//netex:ProductType', ns)).text
    farestructuretype = (root.find('.//netex:FareStructureType', ns)).text
    lineref = root.find('.//netex:LineRef', ns)
    
    return {
        'tariffs': tariffs,
        'fare_structure_elements': fare_structure_elements,
        'usertype': usertype,
        'producttype': producttype,
        'farestructuretype': farestructuretype
    }

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Parse a Netex fares XML file and extract key fare information.")
    parser.add_argument('file_path', help="Path to the Netex fares XML file")

    # Parse command-line arguments
    args = parser.parse_args()
    
    # Parse the Netex fares file
    data = parse_netex_fares(args.file_path)

    # Display extracted information
    print("Tariff Information:")
    for tariff in data['tariffs']:
        print(f"ID: {tariff['tariff_id']}, Name: {tariff['tariff_name']}, Fare Type: {tariff['fare_type']}")

    print("\nFare Structure Elements Information:")
    for element in data['fare_structure_elements']:
        print(f"ID: {element['element_id']}, Name: {element['element_name']}, Type: {element['fare_structure_type']}")
        for matrix in element['distance_matrix_elements']:
            print(f"  Start Zone: {matrix['start_zone']}, End Zone: {matrix['end_zone']}, Price Groups: {', '.join(matrix['price_groups'])}")

    print ('UserType', data['usertype'])
    print ('productType', data['producttype'])
    print ('farestructuretype', data['farestructuretype'])
   
