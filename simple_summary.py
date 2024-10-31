import xml.etree.ElementTree as ET
import argparse
import os
import csv


def parse_netex_fares(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the Netex namespace
    ns = {'netex': 'http://www.netex.org.uk/netex'}

    usertype = (root.find('.//netex:UserType', ns)).text
    
    farestructuretype = (root.find('.//netex:FareStructureType', ns)).text
    line = root.find('.//netex:Line', ns) if root.find('.//netex:Line', ns) is not None else None
    if line is not None:
        line_PublicCode = line.find('.//netex:PublicCode', ns).text if line.find('.//netex:PublicCode', ns) is not None else None
    else:
        line_PublicCode = None

    product = (root.find('.//netex:PreassignedFareProduct', ns))
    productname = (product.find('.//netex:Name', ns)).text
    producttype = (product.find('.//netex:ProductType', ns)).text
    tariff = (root.find('.//netex:Tariff', ns))
    triptype = (tariff.find('.//netex:TripType', ns)).text
    operator = (tariff.find('.//netex:OperatorRef', ns)).get('ref')

    
    return {
        
        'usertype': usertype,
        'producttype': producttype,
        'triptype': triptype,
        'productname': productname,
        'farestructuretype': farestructuretype,
        'linepubliccode':line_PublicCode,
        'operator': operator

    }

if __name__ == "__main__":
 
    # Define the CSV file path
    csv_file_path = 'output.csv'

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Parse a Netex fares XML file and extract key fare information.")
    parser.add_argument('file_dir', help="Path to the Netex fares XML directory")

    # Parse command-line arguments
    args = parser.parse_args()

    dir = args.file_dir

    # print(dir)
    # print(os.listdir(dir))

    # Define the CSV file path
    csv_file_path = 'output.csv'

with open(csv_file_path, mode='w', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)

    # Write the header row (column names)
    writer.writerow(["productname", "productType", "triptype", "UserType", "farestructuretype", "linepubliccode", "operator", "dir" "file"])

    for root, dirs, files in os.walk(dir):
    # for filename in os.listdir(dir):
        # file_path = os.path.join(dir, filename)
        for filename in files:
            file_path = os.path.join(root, filename)
        # if os.path.isfile(file_path):
            print(f"Processing file: {file_path}")

            # Parse the Netex fares file
            data = parse_netex_fares(file_path)

            # Display extracted information
            print ('productname', data['productname'])
            print ('productType', data['producttype'])
            print ('UserType', data['usertype'])
            print ('farestructuretype', data['farestructuretype']),
            print ('linepubliccode', data['linepubliccode']) 

            writer.writerow([data['productname'], data['producttype'],data['triptype'] ,data['usertype'] ,data['farestructuretype'] ,data['linepubliccode'] , data['operator'], root, filename ])
    
