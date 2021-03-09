# Author: Michael Huang

import sys
import time
from os import path
import cv2 as cv
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading


DRESW = 640 # resolution width
DRESH = 480 # res height
DFORMAT = QImage.Format_RGB888 # color space
DSCALE = 2 # display scaling factor
DRATE = 30 # frames per second
DINTERVAL = round(1000/DRATE) # frame refresh interval in msec

# CALIBRATE
class Setup(QWidget):
    nextSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.username = ""
        self.color = (0,0,0)
        self.chatrooms = []
        self.left = 420
        self.top = 420
        self.width = 420
        self.height = 360

    def init(self):
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.userlabel = QLabel("Enter Your Username (max 14 characters)", self)
        self.userlabel.move(20,10)

        self.textbox = QLineEdit(self)
        self.textbox.move(20,30)
        self.textbox.resize(280,40)

        self.button1 = QPushButton('Set Username', self)
        self.button1.move(10,80)
        self.button1.clicked.connect(self.set_username)

        self.chosenname = QLabel("Chosen Username", self)
        self.chosenname.move(140,85)


        self.setcolorlabel = QLabel("Select Color", self)
        self.setcolorlabel.move(20,135)

        self.button2 = QPushButton('Set Color', self)
        self.button2.move(10,150)
        self.button2.clicked.connect(self.color_picker)

        self.colorlabel = QLabel("Chosen Color", self)
        self.colorlabel.move(120,155)


        self.chatroomlabel = QLabel("Enter Chatroom Names (separate using commas w/o spaces)", self)
        self.chatroomlabel.move(20,205)

        self.chatroombox = QLineEdit(self)
        self.chatroombox.move(20,225)
        self.chatroombox.resize(280,40)

        self.button3 = QPushButton('Set Chatrooms', self)
        self.button3.move(10,275)
        self.button3.clicked.connect(self.set_chatrooms)

        self.rooms = QLabel("Chatrooms Not Entered", self)
        self.rooms.move(140,280)


        self.button4 = QPushButton('Next', self)
        self.button4.move(10,320)
        self.button4.clicked.connect(self.next_step)

        self.show()

    def getUserName(self):
        return self.username

    def getRGB(self):
        return self.color

    def getChatrooms(self):
        return self.chatrooms


    def set_username(self):
        self.username = self.textbox.text()
        self.chosenname.setText(self.textbox.text())

    def set_chatrooms(self):
        self.chatrooms = self.chatroombox.text().split(",")
        self.rooms.setText("Chatrooms Entered!")

    def color_picker(self):
        color = QColorDialog.getColor()
        self.colorlabel.setStyleSheet("QWidget { background-color: %s}" % color.name())
        self.color = self.hex_to_rgb(color.name())

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    
    def next_step(self):
        print(self.getUserName())
        print(self.getRGB())
        print(self.getChatrooms())
        self.nextSignal.emit()
        # self.usernameSignal.emit(self.getUserName())
        # self.colorSignal.emit(self.getRGB())
        # self.chatroomsSignal.emit(self.getChatrooms())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Setup()
    ex.init()
    sys.exit(app.exec_())
