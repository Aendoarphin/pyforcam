import logging, requests
from xml.etree import ElementTree as ET
from machines import Machines


class XMLTagExtractor:
    def __init__(self, addresses=None, user_tags=None, user_attributes=None, get_content=False):
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
        try:
            response = requests.get(url)
            if response.status_code == 200:
                xml_content = response.content.decode('utf-8')
                #print(xml_content)
                #print("XML file was fetched and displayed.")
                return xml_content
            else:
                #print(f"Failed to fetch XML. Status code: {response.status_code}")
                pass
        except requests.exceptions.RequestException as e:
            #print(f"Error: {e}")
            pass
            
    def retrieve_cutting_tool_info(self, xml_string, id):
        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Find all CuttingTool elements
        cutting_tools = root.findall('.//{urn:mtconnect.org:MTConnectAssets:1.3}CuttingTool')

        # Loop through each CuttingTool and retrieve the required information
        count = 0
        new_machine = Machines()
        for cutting_tool in cutting_tools:
            #print("---------------------------")
            
            #print(f"CuttingTool: {cutting_tool.attrib.get('serialNumber', 'N/A')}")
            
            # Check if the ToolLife element exists and retrieve its text
            tool_life_element = cutting_tool.find('.//{urn:mtconnect.org:MTConnectAssets:1.3}ToolLife')
            tool_life = tool_life_element.text if tool_life_element is not None else 'N/A'
            #print(f"ToolLife: {tool_life}")

            # Check if the ToolLife element has 'initial' attribute and retrieve it
            initial_life = tool_life_element.attrib.get('initial', 'N/A') if tool_life_element is not None else 'N/A'
            #print(f"Initial ToolLife: {initial_life}")

            # Check if the ProgramToolNumber element exists and retrieve its text
            program_tool_number_element = cutting_tool.find('.//{urn:mtconnect.org:MTConnectAssets:1.3}ProgramToolNumber')
            program_tool_number = program_tool_number_element.text if program_tool_number_element is not None else 'N/A'
            #print(f"ProgramToolNumber: {program_tool_number}")
            
            self.toolLives.append(tool_life)
            self.toolNums.append(program_tool_number)
            self.toolInits.append(initial_life)
            
            #print("---------------------------")
            count += 1
        new_machine.id = id
        new_machine.toolLife = self.toolLives
        new_machine.toolNum = self.toolNums
        new_machine.initial = self.toolInits
        self.machines.append(new_machine)
        
        self.toolLives = []
        self.toolNums = []
        self.toolInits = []
        
        #print("---------------------------")
        #print(f"Tools Analyzed: {count}")
        #print("---------------------------")

    def fetch_data(self, address_list, port, id):
        self.machines = []  # Clear the machines list before processing new data

        count = 0
        for address in address_list:
            self.toolNums = []  # Clear the toolNums list before processing data for a new machine
            self.toolLives = []  # Clear the toolLives list before processing data for a new machine
            self.toolInits = []  # Clear the toolInits list before processing data for a new machine

            url = f"http://{address}:{port}/sample-files" # TEST URL
            
            # url = f"http://{address}:{port}/assets" # REAL URL
            self.retrieve_cutting_tool_info(self.get_xml(url), id)  # Pass the XML content to the method
            id += 1
            count += 1
            
        #print("---------------------------")
        #print(f"Machines analyzed: {count}")
        #print("---------------------------")
        
        for machine in self.machines:
            #print(machine)
            pass

if __name__ == "__main__":
    extractor = XMLTagExtractor()
    list = ["192.168.1.248",
            "192.168.1.248",
            "192.168.1.248",
            "192.168.1.248"]
    extractor.fetch_data(list, "8000", 1)
    
# REMOVE PASSES WHEN ENABLING LOGS
