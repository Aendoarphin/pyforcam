import logging, requests
from xml.etree import ElementTree as ET
from machines import Machines

class XMLTagExtractor:
    def __init__(self, addresses, user_tags, user_attributes=None, get_content=False):
        self.addresses = addresses if isinstance(addresses, list) else [addresses]
        self.user_tags = user_tags
        self.user_attributes = user_attributes
        self.get_content = get_content
        self.machines = []

        # self.namespace_mappings = {
        #     "https://static.staticsave.com/testingforcam/assets2.xml": {
        #         "m": "urn:mtconnect.org:MTConnectAssets:1.3",
        #         "x": "urn:okuma.com:OkumaToolAssets:1.3"
        #     },
        #     "https://static.staticsave.com/testingforcam/assets.xml": {
        #         "m": "urn:mtconnect.org:MTConnectAssets:1.3",
        #         "x": "urn:okuma.com:OkumaToolAssets:1.3"
        #     },
        #     f"http://{addresses}:5000/assets": {
        #         "m": "urn:mtconnect.org:MTConnectAssets:1.3",
        #         "x": "urn:okuma.com:OkumaToolAssets:1.3"
        #     },
        #     # Add more mappings for other addresses if needed
        # }
        
        # Define the namespace mappings for the common namespaces
        common_namespace_mapping = {
            "m": "urn:mtconnect.org:MTConnectAssets:1.3",
            "x": "urn:okuma.com:OkumaToolAssets:1.3"
        }

        # Create a separate namespace mapping for the addresses with a single IP
        single_ip_mapping = {}
        for address in self.addresses:
            single_ip_mapping[f"http:/{address}:5000/assets"] = common_namespace_mapping

        # Combine the two namespace mappings
        self.namespace_mappings = {
            "https://static.staticsave.com/testingforcam/assets2.xml": common_namespace_mapping,
            "https://static.staticsave.com/testingforcam/assets.xml": common_namespace_mapping,
            **single_ip_mapping
            # Add more mappings for other addresses if needed
        }

        self.logger = logging.getLogger(__name__)
        
        # VALUES STORED HERE. INDICES FOR EACH LIST REPRESENT ONE CUTTING TOOL
        self.toolNums = []
        self.toolLives = []
        self.toolInits = []

    def extract_xml_tag_content(self):
        count = 0
        for address in self.addresses:
            # Clear the lists before processing each address
            self.toolNums.clear()
            self.toolLives.clear()
            self.toolInits.clear()

            self.process_address(address)
            new_machine = Machines(count + 1, self.toolNums, self.toolLives, self.toolInits)
            self.machines.append(new_machine)
            count += 1  # Increment the count for the next machine ID

        for machine in self.machines:
            self.logger.info(machine)

    def process_address(self, address):
        # url = f"http://{address}:5000/assets"
        try:
            # Set the custom User-Agent header in the request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            response = requests.get(address)
            # response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.logger.error(f"Failed to retrieve data from address '{address}'")
                return

            content = response.content.decode("utf-8")
            root = ET.fromstring(content)

            if address in self.namespace_mappings:
                namespaces = self.namespace_mappings[address]
            else:
                self.logger.error(f"No namespace mapping found for address '{address}'")
                return

            self.process_user_tags(root, namespaces)

        except requests.RequestException as e:
            self.logger.error(f"Failed to retrieve data from address '{address}'")
            self.logger.exception(e)

    def process_user_tags(self, root, namespaces):
        for tag in self.user_tags:
            target_tags = root.findall(f".//m:{tag}", namespaces)
            self.logger.info(f"Target Tag: <{tag}>")
            
            if not target_tags:
                self.logger.info('Target not found')
                continue
            
            self.logger.info("Target(s) exist")
            for t in target_tags:
                self.logger.info(f"Target: <{tag}>")
                if self.user_attributes:
                    self.process_user_attributes(t)
                    
                if self.get_content:
                    content = t.text
                    if content:
                        extracted_content = content.strip()
                        self.logger.info(f"Content: {extracted_content}")
                        self.store_tool_data(tag, extracted_content)

    def process_user_attributes(self, tag):
        for attribute in self.user_attributes:
            if attribute in tag.attrib:
                self.logger.info(f"Attribute {attribute}: {tag.attrib[attribute]}")
                self.store_tool_att(attribute, tag.attrib[attribute])
                
    def store_tool_data(self, tag, content):
        if tag == "ProgramToolNumber":
            self.toolNums.append(str(content))
        if tag == "ToolLife":
            self.toolLives.append(str(content))
            
    def store_tool_att(self, att, content):
        if att == "initial":
            self.toolInits.append(str(content))

