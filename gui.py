#!/usr/bin/python
import sys
from PySide.QtGui import *
from PySide.QtCore import *
import os
import voting
from time import *
try:
    from SimpleCV import Camera
except:
    print "no simple cv"
from chat_client.pearclient import PearClient as PC
import json
import random

_main_path = "test_images/"
LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024
IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 40


class CryptoPear(QWidget):

    def __init__(self):
        super(CryptoPear, self).__init__()

        self.initUI()

    def listdir(self):
        path = os.getcwd() + '/test_images/'
        files = os.listdir(path)
        return map(lambda f: path + f, files)

    def random_path(self):
        return self.paths[random.randint(0, len(self.paths) - 1)]

    def initUI(self):
        self.paths = self.listdir()
        self.photo_json_list = []
        self.accept_reject_dict = {}
        self.default_image = self.paths.pop(0)
        pixmap = QPixmap(self.default_image).scaledToHeight(200)
        self.lbl = QLabel(self)
        self.lbl.setPixmap(pixmap)
        self.name_label = QLabel(self)

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_to_server)
        self.btn_accept = QPushButton("Yes")
        self.btn_reject = QPushButton("No")
        self.btn_accept.clicked.connect(self.accept_participent)
        self.btn_reject.clicked.connect(self.reject_participent)
        self.btn_accept.setDisabled(True)
        self.btn_reject.setDisabled(True)
        self.btn_accept.hide()
        self.btn_reject.hide()

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.btn_connect)
        hbox.addWidget(self.btn_accept)
        hbox.addWidget(self.btn_reject)

        self.chatbox = QTextEdit(self)
        self.chatbox.setMinimumHeight(400)
        self.chatbox.setReadOnly(True)

        self.text_entry = QTextEdit(self)
        self.text_entry.installEventFilter(self)
        self.btn_submit = QPushButton("Submit")
        self.btn_submit.clicked.connect(self.submit_message)
        self.btn_submit.setDisabled(True)
        text_hbox = QHBoxLayout()
        text_hbox.addWidget(self.text_entry)
        text_hbox.addWidget(self.btn_submit)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.lbl)
        vbox.addWidget(self.name_label)
        vbox.addLayout(hbox)
        vbox.addWidget(self.chatbox)
        vbox.addLayout(text_hbox)
        self.setLayout(vbox)

        #starting x, starting y, width, height
        self.setGeometry(0, 0, 500, 700)
        self.setWindowTitle('CryptoPear')
        self.show()

    def eventFilter(self, obj, event):
        if obj == self.text_entry:
            if isinstance(event, QKeyEvent):
                if event.key() == Qt.Key_Return:
                    if event.type() == QEvent.KeyPress:
                        self.submit_message()
                        return True

        return False

    def get_camera(self):
        try:
            cam = Camera()
            img = cam.getImage()
            img.save("mZOMGGUYS.png")
        except:
            pass
        return voting.encode_image(self.random_path())

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
        self.photo_json_list = json.loads(self.server_handler.photo_data)
        self.btn_accept.show()
        self.btn_reject.show()
        self.btn_connect.hide()
        self.update_photo()
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
        message = self.text_entry.toPlainText().encode('ascii')
        if message:
            self.server_handler.encrypted_send(message+'\n')
            self.text_entry.clear()

    def set_picture(self, file_path):
        image = QImage(file_path)
        if image.isNull():
            QMessageBox.information(self, "Image Viewer",
                    "Cannot load file")
            return

        self.lbl.setPixmap(QPixmap.fromImage(image).scaledToHeight(200))
        self.lbl.adjustSize()

    def update_photo(self):
        self.user_data = self.photo_json_list.pop(0)
        voting.decode_image(self.user_data['photo'], self.user_data['name'])
        path = os.getcwd() + '/test_images/' + self.user_data['name'] + '.jpeg'
        print path
        self.set_picture(path)
        self.name_label.setText('Is this ' + self.user_data['name'] + '?')

    def accept_participent(self):
        self.accept_reject_dict[self.user_data['id']] = True
        if self.photo_json_list:
            self.update_photo()
        else:
            self.server_handler.vote_result(json.dumps(self.accept_reject_dict))
            self.set_picture(self.default_image)
            self.btn_accept.setDisabled(True)
            self.btn_reject.setDisabled(True)
            self.btn_submit.setDisabled(False)
            self.btn_accept.hide()
            self.btn_reject.hide()
            self.btn_connect.hide()
            self.name_label.setText("")

    def reject_participent(self):
        self.accept_reject_dict[self.user_data['id']] = False
        if self.photo_json_list:
            self.update_photo()
        else:
            print self.user_data
            self.server_handler.vote_result(json.dumps(self.accept_reject_dict))
            self.set_picture(self.default_image)
            self.btn_accept.setDisabled(True)
            self.btn_reject.setDisabled(True)
            self.btn_submit.setDisabled(False)
            self.btn_accept.hide()
            self.btn_reject.hide()
            self.btn_connect.hide()
            self.name_label.setText("")

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
                new_messages = "".join(self.server_handler.get_recent_messages())
            except:
                pass
            self.message.emit(new_messages)

def main():
    app = QApplication(sys.argv)
    cp = CryptoPear()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
