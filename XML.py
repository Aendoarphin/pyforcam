import logging
import requests
from xml.etree import ElementTree as ET
from machines import Machines
from PyQt6 import QtCore
import threading
from log import configure_logging

class XMLTagExtractor(QtCore.QObject):
    timed_out = QtCore.pyqtSignal(str)

    def __init__(self, addresses=None, user_tags=None, user_attributes=None, get_content=False):
        super().__init__()
        self.addresses = addresses if isinstance(addresses, list) else [addresses]
        self.user_tags = user_tags
        self.user_attributes = user_attributes
        self.get_content = get_content
        self.machines = []
        self.machine_names = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        configure_logging()  # Call the logging configuration once

    def get_xml(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            xml_content = response.content.decode('utf-8')
            #self.logger.info(f"XML fetched successfully from {url}")
            return xml_content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching XML from {url}: {e}")
            self.timed_out.emit(str(e))
            return

    def retrieve_cutting_tool_info(self, xml_string, id, machine_name):
        root = ET.fromstring(xml_string)
        cutting_tools = root.findall('.//{urn:mtconnect.org:MTConnectAssets:1.3}CuttingTool')

        new_machine = Machines()
        for cutting_tool in cutting_tools:
            tool_life_element = cutting_tool.find('.//{urn:mtconnect.org:MTConnectAssets:1.3}ToolLife')
            tool_life = tool_life_element.text if tool_life_element is not None else 'NULL'
            initial_life = tool_life_element.attrib.get('initial', 'NULL') if tool_life_element is not None else 'NULL'

            program_tool_number_element = cutting_tool.find('.//{urn:mtconnect.org:MTConnectAssets:1.3}ProgramToolNumber')
            program_tool_number = program_tool_number_element.text if program_tool_number_element is not None else 'NULL'

            new_machine.toolLife.append(tool_life)
            new_machine.toolNum.append(program_tool_number)
            new_machine.initial.append(initial_life)
        new_machine.machine_name = machine_name
        new_machine.id = id
        with self.lock:
            # Find the index to insert the new_machine based on its id
            index_to_insert = 0
            while (index_to_insert < len(self.machines)) and (self.machines[index_to_insert].id < id):
                index_to_insert += 1
            
            # Insert the new_machine at the appropriate index
            self.machines.insert(index_to_insert, new_machine)
            
############################## MODULAR URL ##############################################

    def fetch_data(self, address_list, port, id, machine_name_list):
        self.machines = []

        def fetch_thread(address, port, id, machine_name):
            # url = f"http://{address}:{port}/sample-files"  # TEST URL
            url = f"http://{address}:{port}/assets"  # LIVE URL
            try:
                self.retrieve_cutting_tool_info(self.get_xml(url), id, machine_name)
                #self.logger.info(f"Data fetched for machine ID {id} from {url}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching data for machine ID {id} from {url}: {e}")

        # Limit the number of concurrent threads based on server capacity or rate limits
        MAX_CONCURRENT_THREADS = 4

        threads = []
        for address, machine_name in zip(address_list, machine_name_list):
            thread = threading.Thread(target=fetch_thread, args=(address, port, id, machine_name))
            thread.start()
            threads.append(thread)
            id += 1

            # Enforce the maximum number of concurrent threads
            if len(threads) >= MAX_CONCURRENT_THREADS:
                for thread in threads:
                    thread.join()
                threads.clear()

        # Join any remaining threads
        for thread in threads:
            thread.join()
        
        # for machine in self.machines:
        #     print(f"Tool Count: {len(machine.toolNum)} | Initial Count: {len(machine.toolLife)} | ID: {machine.id} | Machine Names: {machine.machine_name}")
            
############################## MODULAR URL ##############################################
    
############################## EXPLICIT URL ##############################################
    # def fetch_thread(self, url, id, machine_name):
    #         try:
    #             self.retrieve_cutting_tool_info(self.get_xml(url), id, machine_name)
    #         except requests.exceptions.RequestException as e:
    #             self.logger.error(f"Error fetching data for machine ID {id} from {url}: {e}")
                
    # def fetch_data(self, url_list, id, machine_name_list):
    #     self.machines = []

    #     MAX_CONCURRENT_THREADS = 4
    #     threads = []

    #     for url, machine_name in zip(url_list, machine_name_list):
    #         thread = threading.Thread(target=self.fetch_thread, args=(url, id, machine_name))
    #         thread.start()
    #         threads.append(thread)
    #         id += 1

    #         if len(threads) >= MAX_CONCURRENT_THREADS:
    #             for thread in threads:
    #                 thread.join()
    #             threads.clear()

    #     for thread in threads:
    #         thread.join()

    #     for machine in self.machines:
    #         print(f"Tool Count: {len(machine.toolNum)} | Initial Count: {len(machine.toolLife)} | ID: {machine.id} | Machine Names: {machine.machine_names}")
    
############################## EXPLICIT URL ##############################################


# # THIS BLOCK IS FOR TESTING PURPOSES
# if __name__ == "__main__":
#     extractor = XMLTagExtractor()
#     address_list = ["http://192.168.1.222:5000/sample-files",
#                     "http://192.168.1.222:5000/sample-files",
#                     "http://192.168.1.222:9000/sample-files",
#                     "http://192.168.1.222:9000/sample-files"]
#     machine_name_list = ["Machine A", "Machine B", "Machine C", "Machine D"]
#     extractor.fetch_data(address_list, 1, machine_name_list)
    
# THIS BLOCK IS FOR TESTING PURPOSES
if __name__ == "__main__":
    extractor = XMLTagExtractor()
    address_list = ["192.168.1.222",
                    "192.168.1.222",
                    "192.168.1.222",
                    "192.168.1.222"]
    machine_name_list = ["Machine A", "Machine B", "Machine C", "Machine D"]
    extractor.fetch_data(address_list, "5000", 1, machine_name_list)



