import sys
import requests
import tempfile
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QMessageBox

class XMLDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.url_label = QLabel("Full URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("http://192.168.1.82:5000/assets")

        self.download_button = QPushButton("Get XML")
        self.download_button.clicked.connect(self.get_xml)

        self.xml_display = QTextEdit()
        self.xml_display.setReadOnly(True)
        self.xml_display.setPlaceholderText("Fetched XML will be displayed here.")

        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_button)
        layout.addWidget(self.xml_display)

        self.setLayout(layout)
        self.setWindowTitle("XML Fetcher")

    def get_xml(self):
        url = self.url_input.text()

        try:
            response = requests.get(url)
            if response.status_code == 200:
                xml_content = response.content.decode('utf-8')
                self.xml_display.setPlainText(xml_content)
                self.show_message("XML file was fetched and displayed.")
            else:
                self.show_message(f"Failed to fetch XML. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.show_message(f"Error: {e}")

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XMLDownloaderApp()
    window.show()
    sys.exit(app.exec())
