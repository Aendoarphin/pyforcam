import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from xml.etree import ElementTree as ET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QTableWidget Demo")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(1)  # Single column for <ToolLife> values
        self.table_widget.setHorizontalHeaderLabels(["ToolLife"])
        layout.addWidget(self.table_widget)

        button = QPushButton("Populate Table")
        button.clicked.connect(self.populate_table)
        layout.addWidget(button)

    def fetch_data_from_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to fetch data from URL: {url}")
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")

    def parse_xml_data(self, data):
        try:
            root = ET.fromstring(data)
            ns_mapping = {
                "m": "urn:mtconnect.org:MTConnectAssets:1.3",
                "x": "urn:okuma.com:OkumaToolAssets:1.3"
            }
            m_namespace = ns_mapping.get("m")
            tool_life_values = root.findall(f".//{{{m_namespace}}}ToolLife")
            return [tl.text.strip() for tl in tool_life_values]
        except ET.ParseError as e:
            print(f"Error parsing XML data: {e}")
            return []

    def populate_table(self):
        url = "https://static.staticsave.com/testingforcam/assets.xml"
        data = self.fetch_data_from_url(url)
        if data:
            tool_life_values = self.parse_xml_data(data)
            self.table_widget.setRowCount(len(tool_life_values))

            for i, value in enumerate(tool_life_values):
                item = QTableWidgetItem(value)
                self.table_widget.setItem(i, 0, item)

    # ... (Rest of the class remains unchanged)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
