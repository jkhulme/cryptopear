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

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        pixmap = QtGui.QPixmap("test_images/test_james.jpeg")
        lbl = QtGui.QLabel(self)
        lbl.setPixmap(pixmap)

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
        vbox.addWidget(lbl)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('CryptoPear')
        self.show()

    def accept_participent(self):
        print "participant accepted"

    def reject_participent(self):
        print "participant rejected"

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
