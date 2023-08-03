import logging
import requests
from xml.etree import ElementTree as ET
from machines import Machines


class XMLTagExtractor:
    def __init__(self, addresses=None, user_tags=None, user_attributes=None, get_content=False):
        """
        Initialize the XMLTagExtractor object.

        Parameters:
            addresses (list or str): A list of IP addresses or a single IP address.
            user_tags (list): A list of user-defined tags to extract from the XML (not used in this code).
            user_attributes (list): A list of user-defined attributes to extract from the XML (not used in this code).
            get_content (bool): Whether to fetch and extract the content of XML tags (not used in this code).
        """
        self.addresses = addresses if isinstance(addresses, list) else [addresses]
        self.user_tags = user_tags
        self.user_attributes = user_attributes
        self.get_content = get_content
        self.machines = []

        self.logger = logging.getLogger(__name__)

        # VALUES STORED HERE. INDICES FOR EACH LIST REPRESENT ONE CUTTING TOOL
        self.toolNums = []
        self.toolLives = []
        self.toolInits = []

    def get_xml(self, url):
        """
        Fetch the XML content from the specified URL.

        Parameters:
            url (str): The URL to fetch the XML content from.

        Returns:
            str: The XML content as a string if successful, otherwise None.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                xml_content = response.content.decode('utf-8')
                return xml_content
            else:
                pass
        except requests.exceptions.RequestException as e:
            pass

    def retrieve_cutting_tool_info(self, xml_string, id):
        """
        Extract cutting tool information from the XML content.

        Parameters:
            xml_string (str): The XML content as a string.
            id (int): The identifier for the machine.

        Note:
            The extracted cutting tool information is stored in the `self.machines` list.
        """
        root = ET.fromstring(xml_string)

        cutting_tools = root.findall('.//{urn:mtconnect.org:MTConnectAssets:1.3}CuttingTool')

        count = 0
        new_machine = Machines()
        for cutting_tool in cutting_tools:
            tool_life_element = cutting_tool.find('.//{urn:mtconnect.org:MTConnectAssets:1.3}ToolLife')
            tool_life = tool_life_element.text if tool_life_element is not None else 'N/A'

            initial_life = tool_life_element.attrib.get('initial', 'N/A') if tool_life_element is not None else 'N/A'

            program_tool_number_element = cutting_tool.find('.//{urn:mtconnect.org:MTConnectAssets:1.3}ProgramToolNumber')
            program_tool_number = program_tool_number_element.text if program_tool_number_element is not None else 'N/A'

            self.toolLives.append(tool_life)
            self.toolNums.append(program_tool_number)
            self.toolInits.append(initial_life)

            count += 1
        new_machine.id = id
        new_machine.toolLife = self.toolLives
        new_machine.toolNum = self.toolNums
        new_machine.initial = self.toolInits
        self.machines.append(new_machine)

        self.toolLives = []
        self.toolNums = []
        self.toolInits = []

    def fetch_data(self, address_list, port, id):
        """
        Fetch data from multiple machines and extract cutting tool information.

        Parameters:
            address_list (list): A list of IP addresses of the machines to fetch data from.
            port (str): The port number for the machine.
            id (int): The starting identifier for the machines.

        Note:
            The extracted cutting tool information for each machine is stored in the `self.machines` list.
        """
        self.machines = []  # Clear the machines list before processing new data

        count = 0
        for address in address_list:
            self.toolNums = []  # Clear the toolNums list before processing data for a new machine
            self.toolLives = []  # Clear the toolLives list before processing data for a new machine
            self.toolInits = []  # Clear the toolInits list before processing data for a new machine

            url = f"http://{address}:{port}/sample-files" # TEST URL

            self.retrieve_cutting_tool_info(self.get_xml(url), id)  # Pass the XML content to the method
            id += 1
            count += 1

        for machine in self.machines:
            pass

# THIS BLOCK IS FOR TESTING PURPOSES
if __name__ == "__main__":
    extractor = XMLTagExtractor()
    list = ["192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248"]
    extractor.fetch_data(list, "8000", 1)
