##
 #  File: gui.py
 # 
 #  Author: Nate Atkinson
 #  
 #  @brief ui and event handling for data/classifiers
 #

PATH = [
        # '../training/classifier_training',
        # '../video_embedder',
        # '../static_ar_exploration',
        # '../img_implanter/mqtt_comms',
        '../envrd/audio',
        # '../envrd/gesture_detector',
        # '../env_reader/image_tracking/hand_tracker'
       ]

import sys
print("path is ")
for p in sys.path: 
    print(p)
print("appending...")
for lib in PATH:
    sys.path.append(lib)
for p in sys.path: 
    print(p)

import time
# from os import path
import cv2 as cv
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading
# import IMU
# import mqtt_message
import audio
# import hand_tracker
# import static_homography
# import gest_classifier

for lib in PATH:
    sys.path.remove(lib)

DRESW = 1280 # resolution width
DRESH = 720 # res height
DFORMAT = QImage.Format_RGB888 # color space
DSCALE = 2 # display scaling factor
DRATE = 30 # frames per second
DINTERVAL = round(1000/DRATE) # frame refresh interval (msec)

ATIMEOUT = 5000 # speech recognition max phrase time (msec)

###################################################################

# @desc
# dump all required signals here 
# (likely won't be needed since signals are threadsafe and can be emitted/received outside thread)
class JobSignals():

    error = pyqtSignal(tuple) # redirect error reporting
    output = pyqtSignal(object) # notify slot of function returned value
    done = pyqtSignal() # notify main thread of completion

# @desc
# utility class for handling multithreading in Qt
# all heavy event-triggered ops should be called through this class
class JobRunner(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(JobRunner, self).__init__()

        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = JobSignals()

    @pyqtSlot()
    def run(self):
        try:
            output = self.function(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.output.emit(output)
        finally:
            self.signals.done.emit()


class MQTTNetObject:
    def __init__(self):
        #TODO
        pass


class IMUSampleObject:
    # def __init__(self, window_length, overlap, sample_period):
    #     self.window_length = window_length #number of Samples
    #     self.classifier    = gest_classifier(2,6*window_length)
    #     self.length_sample = 6
    #     self.data    = [None]*self.length_sample*window_length
    #     self.reading = [None]*self.length_sample*overlap
    #     self.overlap = overlap
    #     self.samples_taken = 0
    #     self.sample_period = sample_period

    #     #initialize sensor
    #     IMU.detectIMU()
    #     if(IMU.BerryIMUversion == 99):
    #         print(" No BerryIMU found...sick nasty")
    #         sys.exit()
    #     IMU.initIMU() # initialize all the relevant sensors

    # def sample(self):
    #     ACCx = IMU.readACCx()
    #     ACCy = IMU.readACCy()
    #     ACCz = IMU.readACCz()
    #     GYRx = IMU.readGYRx()
    #     GYRy = IMU.readGYRy()
    #     GYRz = IMU.readGYRz()
    #     self.reading[self.samples_taken*self.length_sample]      = ACCx
    #     self.reading[self.samples_taken*self.length_sample + 1 ] = ACCy
    #     self.reading[self.samples_taken*self.length_sample + 2 ] = ACCz
    #     self.reading[self.samples_taken*self.length_sample + 3 ] = GYRx
    #     self.reading[self.samples_taken*self.length_sample + 4 ] = GYRy
    #     self.reading[self.samples_taken*self.length_sample + 5 ] = GYRz
        
    #     self.samples_taken += 1

    #     if not(self.samples_taken % self.overlap):
    #         self.data = np.roll(self.data, (self.window_length - self.overlap)*6)
    #         self.data[-self.overlap:] = self.reading
    #         self.samples_taken = 0
    #         self.classifier.classify(self.data) #TODO make event triggering on this result

    # def run(self):
    #     threading.Timer(self.sample_period, self.sample).start()
    pass


class AreaSelectObject:
    def __init__(self):
        #TODO
        pass


class AudioObject(QObject):
    detected_phrase = pyqtSignal(str)
    def __init__(self, keyphrases : dict, parent=None):
        super().__init__(parent)
        self.recognizer = audio.SpeechRecognizer(keyphrases)
        # self.timer = QTimer()
        # self.timer.setSingleShot(True)
        # self.timer.timeout.connect(lambda: self.recognizer.teardown())

    # @desc
    # waits for a keyphrase to be found, then returns the first detected phrase
    def recordDetection(self):
        end = False
        try:
            while(end == False):
                for phrase, found in self.recognizer.phrases.items():
                    if found:
                        self.recognizer.resetDetection(phrase)
                        self.detected_phrase.emit(phrase)
                        self.recognizer.teardown()
                        end = True
        except TypeError:
            pass
        except ValueError:
            pass

    def speechHandler(self):
        # self.timer.start(ATIMEOUT)
        self.recognizer.listenForPhrases()
        self.recordDetection()


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

    # TODO
    # should take member masks 
    def processMasks():
        pass

    # @desc 
    # sets the widget's QImage object, used as a slot for receiving the image_data signal
    def setImage(self, image):
        # self.processMasks()
        self.image = self._array2qimage(image)
        self.setFixedSize(self.image.size())
        # print(self.image.size())
        self.update()

    #### IMAGE PROCESSING SLOTS ####
    # TODO
    def setHomographyMask(self, layer):
        pass

    # TODO
    def setHandTrackMask(self, layer):
        pass

    #### MISC SLOTS ####
    def keyphrasehandler(self, phrase):
        print("FOUND: " + phrase)

    ####

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
        # self.cap.set(3, DRESW)
        # self.cap.set(4, DRESH)
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
# also handles threading
class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # widgets and objects
        self.display = DisplayWidget()
        self.video = TestVideo()
        self.start_button = QPushButton('START')
        self.audio_phrases = {}
        self.audio_recognizer = AudioObject(self.audio_phrases)

        # state machine
        self.state_machine = QStateMachine()

        self.s_start = QState()
        
        self.s_cal = QState()
        self.s_cal_ht = QState(self.s_cal)
        self.s_cal_wave = QState(self.s_cal)
        self.s_cal.setInitialState(self.s_cal_ht)

        self.s_main = QState(childMode=1) # parallel child states
        self.s_img = QState(self.s_main)
        self.s_msg = QState(self.s_main)
        self.s_msg_listen = QState(self.s_msg)
        self.s_msg_send = QState(self.s_msg)
        self.s_msg.setInitialState(self.s_msg_listen)

        # state signals
        

        # signals and slots
        self.video.image_data.connect(lambda x: self.display.setImage(x))
        self.start_button.clicked.connect(self.video.start)
        self.start_button.clicked.connect(lambda: self.deleteWidget(self.start_button))
        self.audio_recognizer.detected_phrase.connect(lambda x: self.display.keyphrasehandler(x))

        # layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.start_button)
        self.setLayout(self.layout)

        # state machine init
        self.state_machine.setInitialState(self.s_cal)
        self.state_machine.addState(self.s_cal)
        self.state_machine.addState(self.s_main)
        self.state_machine.start()

        # threading
        self.threadpool = QThreadPool()

    def deleteWidget(self, widget):
        self.layout.removeWidget(widget)
        widget.deleteLater()
        widget = None

    # @desc
    # handles double click event for all widgets in UI
    def mouseDoubleClickEvent(self, event):
        worker = JobRunner(self.audio_recognizer.speechHandler)
        self.threadpool.start(worker)


# @desc
# initializes all UI widgets
class UI:
    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.window = QMainWindow()
        self.main_widget = MainWidget()
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    someUI = UI()
