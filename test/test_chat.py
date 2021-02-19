import sys

PATH = [
    "src/comms/mqtt",
    "src/gui",
    "src/tools",
    "data/gui"
]

for lib in PATH:
    sys.path.append(lib)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import numpy as np

import chat
import thread
import mqtt_net as mqtt
import cv2 as cv
import time

TOPICS = ['general', "Nate", "Tommy", "Michael", "Nico"]
ROOT = 'data/gui/'
DRESW = 640 # resolution width
DRESH = 480 # res height
DFORMAT = QImage.Format_RGB888 # color space

def sendMessage(chat):
    link = mqtt.MQTTLink(topic='ece180d/MEAT/' + chat, user_id = 'Jake')

    message = {
        'message_type'  :   'text',
        'sender'    :   'Jake', 
        'data'      :   str(np.random.randint(3)),
        'time'      :    {
            'hour': 11,
            'minute': 52,
            'second': 0
            },
        'color' :   (255, 255, 255),
        'emoji' :   []
        }

    link.send(message)

# @desc
# widget for handling a display from an opencv source
class DisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()
        self.mask_homography = None # use set...Mask to replace with data from signal
        self.mask_handtrack = None # use set...Mask to replace with data from signal
        
    # @desc
    # private helper function to convert numpy arrays to Qt image objects
    def _array2qimage(self, image : np.ndarray):
        h, w, c = image.shape
        bpl = w*3 # bytes per line
        image = QImage(image.data, w, h, bpl, DFORMAT)
        image = image.rgbSwapped()
        return image

    # @desc 
    # sets the widget's QImage object, used as a slot for receiving the image_data signal
    def setImage(self, image):
        # self.processMasks()
        self.image = self._array2qimage(image)
        self.image = self.image.scaled(DRESW*4, DRESH*4, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setFixedSize(self.image.size())
        # print(self.image.size())
        self.update()

    #### MISC SLOTS ####
    def keyphrasehandler(self, phrase):
        print("FOUND: " + phrase)

    # @desc
    # handler for Qt's paint event, draws the QImage object on screen
    def paintEvent(self, event):
        p = QPainter(self)
        p.drawImage(0, 0, self.image)
        self.image = QImage()

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.manager = chat.BoardManager('Nico')
        self.display = DisplayWidget()

        # threading
        self.threadpool = QThreadPool()

        for topic in TOPICS:
            self.manager.createBoard(topic)

        funcs = self.manager.listen()
        for func in funcs:
            self.__create_worker__(func)

        self.manager.switch.connect(lambda topic: self.switchDisplayTopic(topic))

        self.switchDisplayTopic('general')

        self.layout = QGridLayout()
        self.setMainLayout()

    def keyPressEvent(self, event):
        super(MainWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_Q:
            sendMessage('general')
        if event.key() == Qt.Key_A:
            sendMessage('Nate')
        if event.key() == Qt.Key_S:
            sendMessage('Tommy')
        if event.key() == Qt.Key_D:
            sendMessage('Michael')
        if event.key() == Qt.Key_W:
            self.manager.switchTopic()
            

    def __create_worker__(self, func):
        try:
            worker = thread.JobRunner(func)
            self.threadpool.start(worker)
        except KeyboardInterrupt:
            worker.setAutoDelete(True)

    def switchDisplayTopic(self, topic):
        path = ROOT + topic + '.jpg'
        image = cv.imread(path)
        self.display.setImage(image)
    
    def setMainLayout(self):
        self.layout.addWidget(self.display, 0, 0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

class testUI:
    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.window = QMainWindow()
        self.main_widget = MainWidget()
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    test = testUI()
    


    
    

    
    