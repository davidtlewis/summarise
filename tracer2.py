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

    def find_distance_matrix_elements(self, start_zone_id):
        """
        Find DistanceMatrixElements for the given FareZone ID.
        """
        elements = []
        for element in self.root.findall(".//netex:DistanceMatrixElement", namespaces=self.ns):
            start_zone_ref = element.find(".//netex:StartTariffZoneRef", namespaces=self.ns)
            if start_zone_ref is not None and start_zone_ref.get("ref") == start_zone_id:
                elements.append(element)
        return elements

    def find_price_for_distance_matrix(self, element):
        """
        Find price information from the PriceGroupRef in DistanceMatrixElement.
        """
        price_group = element.find(".//netex:PriceGroupRef", namespaces=self.ns)
        if price_group is not None:
            return price_group.get("ref")
        return "Unknown price"

    def follow_links_to_prices(self, start_stop_id):
        """
        Traverse from a ScheduledStopPoint to FareZone, then find prices to linked zones.
        """
        print(f"Starting traversal from stop ID: {start_stop_id}")
        
        # Find the FareZone for the initial stop
        fare_zone = self.find_fare_zone_for_stop(start_stop_id)
        if fare_zone is None:
            print(f"No FareZone found for stop ID: {start_stop_id}")
            return
        
        start_zone_id = fare_zone.get("id")
        zone_name = fare_zone.find("netex:Name", namespaces=self.ns).text if fare_zone.find("netex:Name", namespaces=self.ns) is not None else "Unknown Zone"
        print(f"FareZone ID for starting stop: {start_zone_id} - {zone_name}")

        # Find connections from this FareZone in the DistanceMatrix
        connections = self.find_distance_matrix_elements(start_zone_id)
        if not connections:
            print("No connections found from the starting FareZone.")
            return

        # List all reachable zones and their prices
        for conn in connections:
            end_zone_ref = conn.find(".//netex:EndTariffZoneRef", namespaces=self.ns)
            if end_zone_ref is not None:
                end_zone_id = end_zone_ref.get("ref")
                price = self.find_price_for_distance_matrix(conn)
                print(f"Connection to Zone ID: {end_zone_id} with Price: {price}")

# Usage
file_path = '../xml/line8415.xml'
start_stop_id = 'atco:3100Z19886G'  # Example starting ScheduledStopPoint ID
explorer = NeTExFareExplorer(file_path)
explorer.follow_links_to_prices(start_stop_id)
