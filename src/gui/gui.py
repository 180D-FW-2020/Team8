##
 #  File: gui.py
 # 
 #  Author: Nate Atkinson
 #  
 #  @brief ui and event handling for data/classifiers
 #

import sys
import time
from os import path
import cv2 as cv
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading
# import hand_tracker
# import static_homography
# import mqtt_message
# import audio
# import gest_classifier
# import IMU
DRES = 1280,720 # resolution
DFORMAT = QImage.Format_RGB888 # color space
DSCALE = 2 # display scaling factor
DRATE = 30 # frames per second
DINTERVAL = round(1000/DRATE) # frame refresh interval in msec

class MQTTNetObject:
    def __init__(self):
        #TODO
        pass

class IMUSampleObject:
    def __init__(self, window_length, overlap, sample_period):
        self.window_length = window_length #number of Samples
        self.classifier    = gest_classifier(2,6*window_length)
        self.length_sample = 6
        self.data    = [None]*self.length_sample*window_length
        self.reading = [None]*self.length_sample*overlap
        self.overlap = overlap
        self.samples_taken = 0
        self.sample_period = sample_period

        #initialize sensor
        IMU.detectIMU()
        if(IMU.BerryIMUversion == 99):
            print(" No BerryIMU found...sick nasty")
            sys.exit()
        IMU.initIMU() # initialize all the relevant sensors

    def sample(self):
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
        self.reading[self.samples_taken*self.length_sample]      = ACCx
        self.reading[self.samples_taken*self.length_sample + 1 ] = ACCy
        self.reading[self.samples_taken*self.length_sample + 2 ] = ACCz
        self.reading[self.samples_taken*self.length_sample + 3 ] = GYRx
        self.reading[self.samples_taken*self.length_sample + 4 ] = GYRy
        self.reading[self.samples_taken*self.length_sample + 5 ] = GYRz
        
        self.samples_taken += 1

        if not(self.samples_taken % self.overlap):
            self.data = np.roll(self.data, (self.window_length - self.overlap)*6)
            self.data[-self.overlap:] = self.reading
            self.samples_taken = 0
            self.classifier.classify(self.data) #TODO make event triggering on this result

    def run(self):
        threading.Timer(self.sample_period, self.sample).start()


class AreaSelectObject:
    def __init__(self):
        #TODO
        pass

# class AudioObject(audio.SpeechRecognizer):
#     def __init__(self, keyphrases):
#         SpeechRecognizer.__init__(self)
#         self.keyphrases = keyphrases
#         for phrase in self.keyphrases:
#             self.add_keyphrase(self, phrase)
#         pass

class VideoOverlayCarousel:
    def __init__(self):
        pass

# @desc
# widget for handling a display from an opencv source
class DisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()

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
        self.image = self._array2qimage(image)
        self.setFixedSize(self.image.size())
        self.update()

    # @desc
    # handler for Qt's paint event, draws the QImage object on screen
    def paintEvent(self, event):
        p = QPainter(self)
        p.drawImage(0, 0, self.image)
        self.image = QImage()
        
# @desc
# test class for opencv video feed -> replace with any np array
class TestVideo(QObject):
    image_data = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv.VideoCapture(0)
        self.trigger = QBasicTimer()

    # @desc
    # event trigger for an instantaneous event; use when an event overload is not desired
    # or when an event trigger must cause a custom signal to emit
    def start(self):
        self.trigger.start(0, self)

    # @desc
    # handles timer events triggered by this class
    def timerEvent(self, event):
        if(event.timerId() != self.trigger.timerId()):
            print("timer shit fucked up")
            return
            
        read, frame = self.cap.read()
        if read:
            self.image_data.emit(frame)

# @desc
# widget that instantiates all other widgets, sets layout, and connects signals to slots
class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("test UI window") #change name after testing
        self.windowTitleChanged.connect(lambda: self.alertWindowChanged()) # example of event-based flow for updating ui data

        self.display = DisplayWidget()
        self.video = TestVideo()
        self.start_button = QPushButton('START')

        self.video.image_data.connect(lambda x: self.display.setImage(x))
        self.start_button.clicked.connect(self.video.start)

        layout = QVBoxLayout()
        layout.addWidget(self.display)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

    def alertWindowChanged(self):
        print("ALERT")

    # @desc
    # handles double click event for all widgets in UI
    def mouseDoubleClickEvent(self, event):
        self.setWindowTitle("CHANGED")

# @desc
# initializes all UI widgets
class UI:
    def __init__(self):
        # self.MQTTHandler = MQTTNetObject()
        # self.IMUSampler = IMUSampleObject()
        # self.AreaSelector = AreaSelectObject()

        # self.stt_keyphrases = ["testing"] #placeholder, update once default phrases are known
        # self.SpeechToText = AudioObject(self.stt_keyphrases)

        self.qapp = QApplication(sys.argv)
        self.window = QMainWindow()
        self.main_widget = MainWidget()
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    someUI = UI()
