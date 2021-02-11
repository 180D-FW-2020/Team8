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

import chat
import thread
import mqtt
import cv2 as cv
import time

def sendMessage():
    link = mqtt.MQTTLink(topic='ece180d/MEAT/general')

    message = {
        'message_type'  :   'text',
        'sender'    :   'Nico', 
        'color'     :   (255, 0, 0), 
        'data'      :   'This is a second test message.',
        'time'      :    {
            'hour': 11,
            'minute': 52,
            'second': 0
            },
        'color' :   (255, 255, 255),
        'emoji' :   []
        }

    link.send(message)

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.manager = chat.BoardManager('Nico')


        # threading
        self.threadpool = QThreadPool()
        self.__create_worker__(self.manager.listen)

    def keyPressEvent(self, event):
        super(MainWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_Q:
            sendMessage()

    def __create_worker__(self, func):
        try:
            worker = thread.JobRunner(func)
            self.threadpool.start(worker)
        except KeyboardInterrupt:
            worker.setAutoDelete(True)

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
    


    
    

    
    