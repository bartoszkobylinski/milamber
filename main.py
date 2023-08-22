import requests
from PyQt6.QtCore import Qt

from secret_data import MILAMBER_WEBHOOK
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLineEdit, QScrollArea,
                             QTextEdit, QHBoxLayout, QListWidget, QLabel, QListWidgetItem, QLayout, QFrame)
from PyQt6.QtGui import QIcon, QPixmap
import sys


class ChatItem(QWidget):
    def __init__(self, text, is_milamber=False):
        super().__init__()
        layout = QHBoxLayout(self)

        if is_milamber:
            icon_label = QLabel(self)
            pixmap = QPixmap("milamber.icns")
            icon_label.setPixmap(pixmap.scaled(32, 32))
            layout.addWidget(icon_label)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(text)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.text_edit)

        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        def showEvent(self, event):
            super().showEvent(event)
            self.text_edit.setFixedSize(self.text_edit.document().size().toSize())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.milamber_webhook = MILAMBER_WEBHOOK
        self.setWindowTitle("Milamber")
        self.setWindowIcon(QIcon("milamber.icns"))

        central_widget = QWidget(self)
        layout = QVBoxLayout()

        self.chat_list = QListWidget(self)
        layout.addWidget(self.chat_list)

        # Adding QLineEdit for user input
        self.input_field = QLineEdit(self)
        layout.addWidget(self.input_field)

        button = QPushButton("Send", self)
        button.clicked.connect(self.send_to_milamber_webhook)
        layout.addWidget(button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_to_milamber_webhook(self):
        user_text = self.input_field.text()

        user_item = QListWidgetItem(self.chat_list)
        user_widget = ChatItem(user_text)
        user_item.setSizeHint(user_widget.sizeHint())
        self.chat_list.addItem(user_item)
        self.chat_list.setItemWidget(user_item, user_widget)

        url = self.milamber_webhook

        data = {
            "query": user_text,
            "type": "query"
        }
        try:
            response = requests.post(url, json=data)
            response_data = response.json()
            if response.status_code == 200:
                milamber_text = response_data.get('answer')
            else:
                milamber_text = response.status_code

            milamber_item = QListWidgetItem(self.chat_list)
            milamber_widget = ChatItem(milamber_text, is_milamber=True)
            milamber_item.setSizeHint(milamber_widget.sizeHint())
            self.chat_list.addItem(milamber_item)
            self.chat_list.setItemWidget(milamber_item, milamber_widget)

            self.input_field.clear()

        except requests.RequestException as error:
            self.response_text_edit.setText(f"Network error {error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setFixedSize(500, 400)
    window.show()

    app.exec()
