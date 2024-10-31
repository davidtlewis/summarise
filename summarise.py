import xml.etree.ElementTree as ET

def parse_netex_fares(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace (Netex XML files often use namespaces, so adapt this if necessary)
    ns = {'netex': 'http://www.netex.org.uk/netex'}

    # Initialize lists to collect information
    services = []
    fares = []

    # Extracting services information
    for service in root.findall('.//netex:ServiceFrame', ns):
        service_id = service.get('id')
        service_name = service.find('.//netex:Name', ns).text if service.find('.//netex:Name', ns) is not None else None
        services.append({
            'service_id': service_id,
            'service_name': service_name
        })

    # Extracting fares information
    for tariff in root.findall('.//netex:Tariff', ns):
        tariff_id = tariff.get('id')
        tariff_name = tariff.find('.//netex:Name', ns).text if tariff.find('.//netex:Name', ns) is not None else None
        price = tariff.find('.//netex:Price', ns).text if tariff.find('.//netex:Price', ns) is not None else None
        fares.append({
            'tariff_id': tariff_id,
            'tariff_name': tariff_name,
            'price': price
        })

    return {
        'services': services,
        'fares': fares
    }

# Path to the Netex fares XML file
file_path = '../xml/line8415.xml'
data = parse_netex_fares(file_path)

# Displaying extracted information
print("Services Information:")
for service in data['services']:
    print(service)

print("\nFares Information:")
for fare in data['fares']:
    print(fare)
