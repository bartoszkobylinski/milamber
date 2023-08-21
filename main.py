import requests
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLineEdit, QLabel
from PyQt6.QtGui import QIcon
import sys
import os
from dotenv import load_dotenv

load_dotenv(".secret")

MILAMBER_ICON_PATH = os.getenv("MILAMBER_ICON_PATH")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.milamber_webhook = os.getenv("MILAMBER_WEBHOOK")
        self.setWindowTitle("Milamber")
        self.setWindowIcon(QIcon(MILAMBER_ICON_PATH))

        central_widget = QWidget(self)
        layout = QVBoxLayout()

        # Adding QLineEdit for user input
        self.input_field = QLineEdit(self)
        layout.addWidget(self.input_field)

        button = QPushButton("Send")
        button.clicked.connect(self.send_to_milamber_webhook)
        layout.addWidget(button)

        self.response_label = QLabel("Response will appear here", self)
        layout.addWidget(self.response_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_to_milamber_webhook(self):
        query_text = self.input_field.text()
        url = self.milamber_webhook

        data = {
            "query": query_text,
            "type": "query"
        }
        try:
            response = requests.post(url, json=data)
            response_data = response.json()
            if response.status_code == 200:
                self.response_label.setText(f"Response: {response_data.get('answer')}")
            else:
                self.response_label.setText(f"Error {response.status_code}")
        except requests.RequestException as error:
            self.response_label.setText(f"Network error {error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
