import xml.etree.ElementTree as ET

class NeTExFareExplorer:
    def __init__(self, filepath):
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()

    def find_elements_with_id(self, tag, element_id):
        """
        Find elements by tag and ID attribute in the XML.
        """
        return [elem for elem in self.root.iter(tag) if elem.get('id') == element_id]

    def find_referenced_element(self, ref_id):
        """
        Find an element anywhere in the XML tree by an ID reference.
        """
        return self.root.find(f".//*[@id='{ref_id}']")

    def follow_links_to_price(self, start_stop_id, max_depth=5):
        """
        Follow links starting from a stop to traverse through zones to reach prices.
        Limits the depth to avoid infinite loops.
        """
        stop = self.find_referenced_element(start_stop_id)
        if not stop:
            print(f"Stop with ID {start_stop_id} not found.")
            return

        print(f"Starting from Stop ID: {start_stop_id}")
        visited = set()
        path = []

        def traverse(element, depth=0):
            if depth > max_depth:
                return

            # Prevent circular references by keeping track of visited nodes
            if element.get('id') in visited:
                return
            visited.add(element.get('id'))

            # Append element details to the path
            path.append((element.tag, element.get('id'), element.get('name', 'Unknown')))

            # Search for fare-related elements or links
            if 'Price' in element.tag:
                print(" -> ".join(f"{tag} ({name})" for tag, _, name in path), f"-> Price: {element.text}")
                return

            # Traverse linked elements by checking for references
            for child in element:
                ref_id = child.get('ref')
                if ref_id:
                    referenced_elem = self.find_referenced_element(ref_id)
                    if referenced_elem:
                        traverse(referenced_elem, depth + 1)

            # Backtrack the path
            path.pop()

        traverse(stop)

# Usage
file_path = '../xml/line8415.xml'
start_stop_id = 'atco:3100U186131'  # Replace with the actual starting stop ID
explorer = NeTExFareExplorer(file_path)
explorer.follow_links_to_price(start_stop_id)
