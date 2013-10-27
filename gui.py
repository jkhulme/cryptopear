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
import rsa
import base64
from event_printer import handle_event_json

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

    def get_pubkey(self):
        return 'abc'

    def get_json(self):
        data = [{ 'name':self.get_user(), 'photo':self.get_camera(), 'publicKey':self.get_pubkey() }]
        data_string = json.dumps(data)
        return data_string

    def connect_to_server(self):
        self.server_handler = ServerHandler()
        self.server_handler.send_message(self.get_json())
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
            self.server_handler.send_message(message)
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
                new_messages = self.server_handler.receive_messages()
            except:
                pass
            self.message.emit(new_messages)
            sleep(1)

class ServerHandler(object):

    def __init__(self):
        if True:
            DESTINATION = '198.211.120.146'
        else:
            DESTINATION = LOCALHOST

        self.server = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
        self.server.connect((DESTINATION, PORT))

        self.messages = []

        self.pub, self.pri = rsa.newkeys(2048, poolsize=4)
        self.server.send(base64.b64encode(self.pub._save_pkcs1_pem()) + "\n")
        data = self.server.recv(BUFFER_S)
        self.server_pub = base64.b64decode(data)

    def __decrypt__(self, data):
        return rsa.decrypt(base64.b64decode(data), self.pri)

    def send_message(self, outgoing_message):
        self.server.send(outgoing_message+'\n')

    def receive_messages(self):
        try:
            # Parse received json data
            data = self.server.recv(BUFFER_S)
            parsed = json.loads(self.__decrypt__(data))
        except ValueError:
            print "Value Error"

        message = handle_event_json(parsed)
        self.messages.append(message)
        return "".join(self.messages[-MESSAGE_LIMIT:])

def main():
    app = QApplication(sys.argv)
    cp = CryptoPear()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
