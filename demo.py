import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Web Browser")
        self.setGeometry(100, 100, 600, 400)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL here")
        self.url_input.returnPressed.connect(self.load_url)

        self.load_button = QPushButton("Load", self)
        self.load_button.clicked.connect(self.load_url)

        self.content_label = QLabel(self)
        self.content_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.load_button)
        layout.addWidget(self.content_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_url(self):
        url = self.url_input.text()
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            content = response.text
            self.content_label.setText(content)
        except requests.exceptions.RequestException as e:
            self.content_label.setText(f"Error loading URL: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WebBrowser()
    browser.show()
    sys.exit(app.exec())
