#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PySide.QtGui import *
from PySide.QtCore import *
import os
import socket as sok
from time import *

_main_path = "test_images/"
LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024
IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 40


class CryptoPear(QWidget):

    def __init__(self):
        super(CryptoPear, self).__init__()

        self.initUI()

    def list_files(self):
        path = '/Users/james/projects/cryptopear/test_images/'
        files = os.listdir(path)
        return map(lambda f: path + f, files)

    def initUI(self):
        self.server_handler = ServerHandler()
        self.paths = self.list_files()

        pixmap = QPixmap(self.paths.pop(0)).scaledToHeight(200)
        self.lbl = QLabel(self)
        self.lbl.setPixmap(pixmap)

        btn_accept = QPushButton("Accept")
        btn_reject = QPushButton("Reject")
        btn_accept.clicked.connect(self.accept_participent)
        btn_reject.clicked.connect(self.reject_participent)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_accept)
        hbox.addWidget(btn_reject)

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

        self.thread = MessageThread(self.chatbox, self.server_handler)
        self.thread.started.connect(self.started)
        self.thread.finished.connect(self.finished)
        self.thread.terminated.connect(self.terminated)
        self.handletoggle()

    def handletoggle(self):
        if self.thread.isRunning():
            self.thread.exiting=True
            while self.thread.isRunning():
                sleep(0.5)
                continue
        else:
            self.thread.exiting=False
            self.thread.start()
            while not self.thread.isRunning():
                sleep(0.5)
                continue

    def started(self):
        print('Continuous batch started')

    def finished(self):
        print('Continuous batch stopped')

    def terminated(self):
        print('Continuous batch terminated')

    def submit_message(self):
        self.server_handler.send_message(self.text_entry.toPlainText())
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

class MessageThread(QThread):

    def __init__(self, chatbox, server_handler):
        super(MessageThread, self).__init__()
        self.chatbox = chatbox
        self.server_handler = server_handler

    def run(self):
        """
        self.chatbox.setReadOnly(False)
        self.chatbox.clear()
        self.chatbox.append(new_messages)
        self.chatbox.setReadOnly(True)
        """
        self.exec_()

    def exec_(self):
        while True:
            print "foobar"
            new_messages = self.server_handler.receive_messages()
            print new_messages
            #sleep(5)

class ServerHandler(object):

    def __init__(self):
        if True:
            DESTINATION = '198.211.120.146'
        else:
            DESTINATION = LOCALHOST

        self.server = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
        self.server.connect((DESTINATION, PORT))
        self.server.setblocking(0)

        self.server.send("The magic word\n")
        self.messages = []

    def send_message(self, outgoing_message):
        self.server.send(outgoing_message+'\n')

    def receive_messages(self):
        data = self.server.recv(BUFFER_S)
        self.messages.append(data)
        return "".join(self.messages[-MESSAGE_LIMIT:])

def main():
    app = QApplication(sys.argv)
    cp = CryptoPear()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
