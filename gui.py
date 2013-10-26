#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PySide import QtGui
import os
import socket as sok
import select
import string

_main_path = "test_images/"
LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024
IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 40


class CryptoPear(QtGui.QWidget):

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

        pixmap = QtGui.QPixmap(self.paths.pop(0)).scaledToHeight(200)
        self.lbl = QtGui.QLabel(self)
        self.lbl.setPixmap(pixmap)

        btn_accept = QtGui.QPushButton("Accept")
        btn_reject = QtGui.QPushButton("Reject")
        btn_accept.clicked.connect(self.accept_participent)
        btn_reject.clicked.connect(self.reject_participent)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_accept)
        hbox.addWidget(btn_reject)

        chatbox = QtGui.QTextEdit(self)
        chatbox.setMinimumHeight(400)
        chatbox.setReadOnly(True)

        text_entry = QtGui.QTextEdit(self)
        btn_submit = QtGui.QPushButton("Submit")
        btn_submit.clicked.connect(self.submit_message)
        text_hbox = QtGui.QHBoxLayout()
        text_hbox.addWidget(text_entry)
        text_hbox.addWidget(btn_submit)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.lbl)
        vbox.addLayout(hbox)
        vbox.addWidget(chatbox)
        vbox.addLayout(text_hbox)
        self.setLayout(vbox)

        #starting x, starting y, width, height
        self.setGeometry(0, 0, 500, 700)
        self.setWindowTitle('CryptoPear')
        self.show()

    def submit_message(self):
        self.server_handler.send_message("I am a robot beep beep")

    def set_picture(self, file_path):
        image = QtGui.QImage(file_path)
        if image.isNull():
            QtGui.QMessageBox.information(self, "Image Viewer",
                    "Cannot load file")
            return

        self.lbl.setPixmap(QtGui.QPixmap.fromImage(image).scaledToHeight(200))
        self.lbl.adjustSize()

    def accept_participent(self):
        self.set_picture(self.paths.pop(0))

    def reject_participent(self):
        print "participant rejected"

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

    def send_message(self, outgoing_message):
        print outgoing_message
        self.server.send(outgoing_message)

def main():

    app = QtGui.QApplication(sys.argv)
    cp = CryptoPear()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
