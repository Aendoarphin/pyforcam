import logging
import requests
from xml.etree import ElementTree as ET
from machines import Machines
from PyQt6 import QtCore

class XMLTagExtractor (QtCore.QObject):
    timed_out = QtCore.pyqtSignal(str)
    def __init__(self, addresses=None, user_tags=None, user_attributes=None, get_content=False):
        super().__init__()
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
                print(response.status_code)
                return xml_content
            else:
                pass
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            self.timed_out.emit(str(e))
            return

    def retrieve_cutting_tool_info(self, xml_string, id):
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
        self.machines = []

        count = 0
        for address in address_list:
            self.toolNums = [] 
            self.toolLives = []
            self.toolInits = []

            # url = f"http://{address}:{port}/sample-files" # TEST URL
            url = f"http://{address}:{port}/assets" # LIVE URL

            try:
                self.retrieve_cutting_tool_info(self.get_xml(url), id)
                id += 1
                count += 1
            except TypeError as e:
                print(e)

        for machine in self.machines:
            pass

# THIS BLOCK IS FOR TESTING PURPOSES
# if __name__ == "__main__":
#     extractor = XMLTagExtractor()
#     list = ["192.168.1.248",
#             "192.168.1.248",
#             "192.168.1.248",
#             "192.168.1.248"]
#     extractor.fetch_data(list, "8000", 1)
