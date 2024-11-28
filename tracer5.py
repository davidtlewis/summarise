from lxml import etree
import re
import argparse


def cleanse(label):
    return re.sub(r'^.*?}','',label)

def find_fare_zone_for_stop(stop_id):
    """
    Locate the FareZone containing the specified ScheduledStopPoint by navigating upwards.
    """
    # Find the ScheduledStopPointRef element with the specified stop_id
    stop_ref = tree.xpath(f"//netex:ScheduledStopPointRef[@ref='{stop_id}']", namespaces= ns)
    
    # If the stop reference is not found, return None
    if not stop_ref:
        return None
    
    # Get the containing FareZone by moving up to the parent
    fare_zone = stop_ref[0].getparent().getparent()  # Move up two levels to the FareZone. TO DO make this more recursive and resilient

    return fare_zone

def find_first_distance_matrix_element( start_zone_id):
    """
    Find the first DistanceMatrixElement for the given FareZone ID.
    """
    # Find DistanceMatrixElement with matching StartTariffZoneRef
    element =  tree.xpath(f"//netex:DistanceMatrixElement[netex:StartTariffZoneRef[@ref='{start_zone_id}']]", namespaces= ns)
    
    # Return the first match if available
    return element[0] if element else None

def find_containing_fse_unused(obj_ref):
    # get all fareStructureElement objects
    tariff = tree.find(".//netex:Tariff", namespaces= ns)
    fareStructureElements = tariff.findall(".//netex:FareStructureElement", namespaces= ns)
    print(f"found {len(fareStructureElements)} fareStructureElements")

    for fareStructureElement in fareStructureElements:
        elements = fareStructureElement.xpath(f".//netex:*[@ref='{obj_ref.get('id')}']", namespaces= ns)
        
        for element in elements:
            print(f"found {cleanse(obj_ref.tag)} in  {cleanse(element.tag)} in FareStructureElement {fareStructureElement.get('id')}")
            return(element)
        
    return None
   
    # Return the first match if available
    # return elements[0] if elements else None


def find_containing_fse(obj_ref):
    if obj_ref.tag == "fateStructureElement":
        # pull up we are back at the FSE 
        return None
    elements = tree.xpath(f".//netex:*[@ref='{obj_ref.get('id')}']", namespaces= ns)
    print(f"found {len(elements)} references to {obj_ref}.  Target object is {elements[0]}")
    # iterating up the chain
    focus = elements[0]
    while focus.tag != "{http://www.netex.org.uk/netex}FareStructureElement":
        parent = focus.getparent()
        print(f"parent of {cleanse(focus.tag)} is {cleanse(parent.tag)}")
        focus = parent
          

def find_price_group_for_distance_matrix( element):
    # Find price group information from the PriceGroupRef in DistanceMatrixElement.
    price_group_ref = element.find(".//netex:PriceGroupRef", namespaces= ns)
    
    if price_group_ref is not None:
        ref = price_group_ref.get('ref')
        price_group =  tree.xpath(f".//netex:PriceGroup[@id='{ref}']", namespaces= ns)
        return price_group[0] if price_group else None
    return "No price group"

def find_amount_for_price_group( element):
    amount = element.find(".//netex:Amount", namespaces= ns)
    price_holder_type = amount.getparent().tag
    price_holder_id = amount.getparent().get('id')
    return amount.text, price_holder_type, price_holder_id

def follow_single_link_to_price( start_stop_id):
    # Trace a single path from a ScheduledStopPoint to the first price found, printing all linking objects.
    path = []  # Track path of elements for tracing purposes
    print(f"Starting traversal from stop ID: {start_stop_id}")
    return
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="within a single netex file, trace from a stop through to an assocoiated fare price to check the structure of the xml..")
    parser.add_argument('-f','--file_path', help="Netex fares XML file")
    parser.add_argument('-s','--start_stop', help="Start stop id")
    parser.add_argument('-e','--end_stop', help="End stop id")

    # Parse command-line arguments
    args = parser.parse_args()

    file_path = args.file_path
    start_stop_id = args.start_stop
    end_stop_id = args.end_stop

    print(file_path)
    print(start_stop_id)
    print(end_stop_id)

    tree = etree.parse(file_path)
    ns = {'netex': 'http://www.netex.org.uk/netex'}  # Define the namespace

    path = []  # Track path of elements for tracing purposes

    if start_stop_id is None:
        # find a stop, any stop
        start_stop_id = tree.find(".//netex:ScheduledStopPoint", namespaces= ns).get('id')

    print(f"Starting traversal from stop ID: {start_stop_id}")
    # Step 1: Find the FareZone containing the stop
    fare_zone =  find_fare_zone_for_stop(start_stop_id)
    if fare_zone is None:
        print(f"No FareZone found for stop ID: {start_stop_id}")
        quit()
    
    start_zone_id = fare_zone.get("id")
    zone_name = fare_zone.find("netex:Name", namespaces= ns).text if fare_zone.find("netex:Name", namespaces= ns) is not None else "Unknown Zone"
    path.append((fare_zone.tag, start_zone_id, zone_name))
    print(f"Found FareZone for stop: {start_zone_id} - {zone_name}")

    # Step 2  find anything containing ref to the zone in a farestructurelement and show the path back up to FSE
    find_containing_fse(fare_zone)
    
    # Step 3: Find the first DistanceMatrixElement for this FareZone
    # first try for case of a OD matrix
    distance_matrix_element =  find_first_distance_matrix_element(start_zone_id)
    if distance_matrix_element is None:
        print("No DistanceMatrixElement found from the starting FareZone.")
        quit()

    # Get end zone and price
    end_zone_ref = distance_matrix_element.find(".//netex:EndTariffZoneRef", namespaces= ns)
    if end_zone_ref is None:
        print("No end zone reference found in DistanceMatrixElement.")
        quit()

    end_zone_id = end_zone_ref.get("ref")

    # Add DistanceMatrixElement to path
    path.append((distance_matrix_element.tag, distance_matrix_element.get("id"),f"Example To Zone ID: {end_zone_id}"))

    price_group =  find_price_group_for_distance_matrix(distance_matrix_element)
    
    if price_group == "No price group":
        print("No price_group found price_group.")
        quit()
    
    # Add PriceGroup to path
    path.append((price_group.tag, price_group.get("id"), ''))

    amount, price_holder_type, price_holder_id =  find_amount_for_price_group(price_group)

    path.append((price_holder_type, price_holder_id,amount))

    # Step 3: Output the trace path
    print("Trace Path:")
    for tag, elem_id, details in path:
        # trim off the ns
        tagname = re.sub(r'^.*?}','',tag)
        print(f">>>{tagname} (ID: {elem_id}): {details}")