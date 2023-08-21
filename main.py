import requests
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.milamber_webhook = os.getenv("MILAMBER_WEBHOOK")
        self.setWindowTitle("Milamber")

        central_widget = QWidget(self)
        layout = QVBoxLayout()
        button = QPushButton("Send")
        button.clicked.connect(self.send_to_milamber_webhook)
        layout.addWidget(button)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_to_milamber_webhook(self):
        url = self.milamber_webhook

        data = {
            "query": "Hi, from the other side?",
            "type": "query"
        }

        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Succesfully sent data to webhook")
        else:
            print(f"Something went wrong: {response.status_code}")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
