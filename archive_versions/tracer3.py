import xml.etree.ElementTree as ET

class NeTExFareExplorer:
    def __init__(self, filepath):
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        self.ns = {'netex': 'http://www.netex.org.uk/netex'}  # Define the namespace

    def find_fare_zone_for_stop(self, stop_id):
        """
        Locate the FareZone containing the specified ScheduledStopPoint.
        """
        for zone in self.root.findall(".//netex:FareZone", namespaces=self.ns):
            for member in zone.findall(".//netex:ScheduledStopPointRef", namespaces=self.ns):
                if member.get("ref") == stop_id:
                    return zone
        return None

    def find_first_distance_matrix_element(self, start_zone_id):
        """
        Find the first DistanceMatrixElement for the given FareZone ID and stop once found.
        """
        for element in self.root.findall(".//netex:DistanceMatrixElement", namespaces=self.ns):
            start_zone_ref = element.find(".//netex:StartTariffZoneRef", namespaces=self.ns)
            if start_zone_ref is not None and start_zone_ref.get("ref") == start_zone_id:
                return element
        return None

    def find_price_for_distance_matrix(self, element):
        """
        Find price information from the PriceGroupRef in DistanceMatrixElement.
        """
        price_group = element.find(".//netex:PriceGroupRef", namespaces=self.ns)
        if price_group is not None:
            return price_group.get("ref")
        return "Unknown price"

    def follow_single_link_to_price(self, start_stop_id):
        """
        Trace a single path from a ScheduledStopPoint to the first price found, printing all linking objects.
        """
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
        price = self.find_price_for_distance_matrix(distance_matrix_element)

        # Add DistanceMatrixElement to path
        path.append((distance_matrix_element.tag, distance_matrix_element.get("id"), f"To Zone ID: {end_zone_id}, Price: {price}"))

        # Step 3: Output the trace path
        print("Trace Path:")
        for tag, elem_id, details in path:
            print(f"{tag} (ID: {elem_id}): {details}")

# Usage
file_path = '../xml/line8415.xml'
start_stop_id = 'atco:3100Z19886G'  # Example starting ScheduledStopPoint ID
explorer = NeTExFareExplorer(file_path)
explorer.follow_single_link_to_price(start_stop_id)
