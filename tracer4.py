from lxml import etree

class NeTExFareExplorer:
    def __init__(self, filepath):
        self.tree = etree.parse(filepath)
        self.ns = {'netex': 'http://www.netex.org.uk/netex'}  # Define the namespace

    def find_fare_zone_for_stop(self, stop_id):
        """
        Locate the FareZone containing the specified ScheduledStopPoint by navigating upwards.
        """
        # Find the ScheduledStopPointRef element with the specified stop_id
        stop_ref = self.tree.xpath(f"//netex:ScheduledStopPointRef[@ref='{stop_id}']", namespaces=self.ns)
        
        # If the stop reference is not found, return None
        if not stop_ref:
            return None
        
        # Get the containing FareZone by moving up to the parent
        fare_zone = stop_ref[0].getparent().getparent()  # Move up two levels to the FareZone
        return fare_zone

    def find_first_distance_matrix_element(self, start_zone_id):
        """
        Find the first DistanceMatrixElement for the given FareZone ID.
        """
        # Find DistanceMatrixElement with matching StartTariffZoneRef
        element = self.tree.xpath(f"//netex:DistanceMatrixElement[netex:StartTariffZoneRef[@ref='{start_zone_id}']]", namespaces=self.ns)
        
        # Return the first match if available
        return element[0] if element else None

    def find_price_group_for_distance_matrix(self, element):
        # Find price group information from the PriceGroupRef in DistanceMatrixElement.
        price_group_ref = element.find(".//netex:PriceGroupRef", namespaces=self.ns)
        
        if price_group_ref is not None:
            ref = price_group_ref.get('ref')
            price_group = self.tree.xpath(f".//netex:PriceGroup[@id='{ref}']", namespaces=self.ns)
            return price_group[0] if price_group else None
        return "Unknown price group"

    def find_amount_for_price_group(self, element):
        amount = element.find(".//netex:Amount", namespaces=self.ns)
        price_holder_type = amount.getparent().tag
        price_holder_id = amount.getparent().get('id')
        return amount.text, price_holder_type, price_holder_id


    def follow_single_link_to_price(self, start_stop_id):
        # Trace a single path from a ScheduledStopPoint to the first price found, printing all linking objects.
        path = []  # Track path of elements for tracing purposes
        print(f"Starting traversal from stop ID: {start_stop_id}")
        
        # Step 1: Find the FareZone containing the stop
        fare_zone = self.find_fare_zone_for_stop(start_stop_id)
        if fare_zone is None:
            print(f"No FareZone found for stop ID: {start_stop_id}")
            return
        
        start_zone_id = fare_zone.get("id")
        zone_name = fare_zone.find("netex:Name", namespaces=self.ns).text if fare_zone.find("netex:Name", namespaces=self.ns) is not None else "Unknown Zone"
        path.append((fare_zone.tag, start_zone_id, zone_name))
        print(f"Found FareZone for stop: {start_zone_id} - {zone_name}")

        # Step 2: Find the first DistanceMatrixElement for this FareZone
        distance_matrix_element = self.find_first_distance_matrix_element(start_zone_id)
        if distance_matrix_element is None:
            print("No DistanceMatrixElement found from the starting FareZone.")
            return

        # Get end zone and price
        end_zone_ref = distance_matrix_element.find(".//netex:EndTariffZoneRef", namespaces=self.ns)
        if end_zone_ref is None:
            print("No end zone reference found in DistanceMatrixElement.")
            return
        end_zone_id = end_zone_ref.get("ref")

        # Add DistanceMatrixElement to path
        path.append((distance_matrix_element.tag, distance_matrix_element.get("id"),f"using to Zone ID: {end_zone_id}"))

        
        
        price_group = self.find_price_group_for_distance_matrix(distance_matrix_element)

        # Add PriceGroup to path
        path.append((price_group.tag, price_group.get("id"), ''))

        amount, price_holder_type, price_holder_id = self.find_amount_for_price_group(price_group)

        path.append((price_holder_type, price_holder_id,amount))


        # Step 3: Output the trace path
        print("Trace Path:")
        for tag, elem_id, details in path:
            print(f">>>{tag} (ID: {elem_id}): {details}")

# Usage
file_path = '../xml/GNEL_1_Outbound_AdultSingle.xml'
start_stop_id = 'atco:410000041010'  # Example starting ScheduledStopPoint ID
explorer = NeTExFareExplorer(file_path)
explorer.follow_single_link_to_price(start_stop_id)
