#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PySide tutorial

In this example, we position two push
buttons in the bottom-right corner
of the window.

author: Jan Bodnar
website: zetcode.com
last edited: August 2011
"""

import sys
from PySide import QtGui
from os import listdir

_main_path = "test_images/"

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def list_files(self):
        path = '/Users/james/projects/cryptopear/test_images/'
        files = listdir(path)
        return map(lambda f: path + f, files)

    def initUI(self):

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

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.lbl)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        #starting x, starting y, width, height
        self.setGeometry(0, 0, 500, 300)
        self.setWindowTitle('CryptoPear')
        self.show()

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

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
