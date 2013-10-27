#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PySide.QtGui import *
from PySide.QtCore import *
import os
import voting
import socket as sok
from time import *
try:
    from SimpleCV import Camera
except:
    print "no simple cv"
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from event_printer import handle_event_json
from chat_client.pearclient import PearClient as PC

_main_path = "test_images/"
LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024
IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 40


class CryptoPear(QWidget):

    def __init__(self):
        super(CryptoPear, self).__init__()

        self.initUI()

    def list_files(self):
        path = os.getcwd() + '/test_images/'
        files = os.listdir(path)
        return map(lambda f: path + f, files)

    def initUI(self):
        self.paths = self.list_files()

        pixmap = QPixmap(self.paths.pop(0)).scaledToHeight(200)
        self.lbl = QLabel(self)
        self.lbl.setPixmap(pixmap)

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_to_server)
        self.btn_accept = QPushButton("Accept")
        self.btn_reject = QPushButton("Reject")
        self.btn_accept.clicked.connect(self.accept_participent)
        self.btn_reject.clicked.connect(self.reject_participent)
        self.btn_accept.setDisabled(True)
        self.btn_reject.setDisabled(True)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.btn_connect)
        hbox.addWidget(self.btn_accept)
        hbox.addWidget(self.btn_reject)

        self.chatbox = QTextEdit(self)
        self.chatbox.setMinimumHeight(400)
        self.chatbox.setReadOnly(True)

        self.text_entry = QTextEdit(self)
        btn_submit = QPushButton("Submit")
        btn_submit.clicked.connect(self.submit_message)
        text_hbox = QHBoxLayout()
        text_hbox.addWidget(self.text_entry)
        text_hbox.addWidget(btn_submit)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.lbl)
        vbox.addLayout(hbox)
        vbox.addWidget(self.chatbox)
        vbox.addLayout(text_hbox)
        self.setLayout(vbox)

        #starting x, starting y, width, height
        self.setGeometry(0, 0, 500, 700)
        self.setWindowTitle('CryptoPear')
        self.show()

    def get_camera(self):
        try:
            cam = Camera()
            img = cam.getImage()
            img.save("mZOMGGUYS.png")
        except:
            pass
        return voting.encode_image("test_images/test_james.jpeg")

    def get_user(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog',
            'Enter your name:')
        if ok:
            return text
        else:
            return None

    def get_json_dict(self):
        data = { 'name':self.get_user(), 'photo':self.get_camera()}
        return data

    def connect_to_server(self):
        self.server_handler = PC("198.211.120.146").ident(self.get_json_dict())
        self.btn_accept.setDisabled(False)
        self.btn_reject.setDisabled(False)
        self.btn_connect.setDisabled(True)

        self.thread = MessageThread(self.chatbox, self.server_handler)
        self.thread.message.connect(self.append_messages, Qt.QueuedConnection)
        self.handletoggle()

    def append_messages(self, messages):
        if messages:
            self.chatbox.setTextColor('red')
            self.chatbox.setReadOnly(False)
            self.chatbox.clear()
            self.chatbox.append(messages)
            self.chatbox.setReadOnly(True)

    def handletoggle(self):
        if self.thread.isRunning():
            self.thread.exiting=True
        else:
            self.thread.exiting=False
            self.thread.start()

    def submit_message(self):
        message = self.text_entry.toPlainText()
        if message:
            self.server_handler.encrypted_send(message)
            self.text_entry.clear()

    def set_picture(self, file_path):
        image = QImage(file_path)
        if image.isNull():
            QMessageBox.information(self, "Image Viewer",
                    "Cannot load file")
            return

        self.lbl.setPixmap(QPixmap.fromImage(image).scaledToHeight(200))
        self.lbl.adjustSize()

    def accept_participent(self):
        self.set_picture(self.paths.pop(0))

    def reject_participent(self):
        print "participant rejected"

    def pretty_json(self, msg_json):
        return msg_json

class MessageThread(QThread):

    message = Signal(str)

    def __init__(self, chatbox, server_handler):
        super(MessageThread, self).__init__()
        self.chatbox = chatbox
        self.server_handler = server_handler

    def run(self):
        while True:
            new_messages = None
            try:
                new_messages = self.server_handler.decrypted_recieve()
            except:
                pass
            self.message.emit(new_messages)
            sleep(1)

def main():
    app = QApplication(sys.argv)
    cp = CryptoPear()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
