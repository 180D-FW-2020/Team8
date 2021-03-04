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

DRESW = 1280 # resolution width
DRESH = 720 # res height
DFORMAT = QImage.Format_RGB888 # color space
DSCALE = 2 # display scaling factor
DRATE = 30 # frames per second
DINTERVAL = round(1000/DRATE) # frame refresh interval in msec

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
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, DRESW)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, DRESH)
        self.trigger = QBasicTimer()
        self.overlayer = ImageOverlayCarousel()
        self.enteredstate = 0
        self.index = 0

    # @desc
    # event trigger for an instantaneous event; use when an event overload is not desired
    # or when an event trigger must cause a custom signal to emit
    def start(self):
        self.trigger.start(0, self)

    def next(self):
        self.enteredstate = not self.enteredstate
    
    def rotateCarousel(self):
        self.overlayer.next()

    # @desc
    # handles timer events triggered by this class
    def timerEvent(self, event):
        if(event.timerId() != self.trigger.timerId()):
            print("timer shit fucked up")
            return
        
        read, frame = self.cap.read()
        if read and self.enteredstate == 0:
            self.image_data.emit(frame)
        else:
            self.image_data.emit(self.overlayer.run(frame))


# @desc
# class for opencv image carousel using ar overlay
class ImageOverlayCarousel(QObject):
    out_image = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = cv.imread('model2.png')
        self.overlay = [cv.imread('chat1.jpg'), cv.imread('chat2.jpg')]
        self.trigger = QBasicTimer()
        self.counter = 0
        self.index = 0

    # @desc
    # event trigger for an instantaneous event; use when an event overload is not desired
    # or when an event trigger must cause a custom signal to emit
    def start(self):
        self.trigger.start(0, self)

    def next(self):
        if self.index != len(self.overlay) - 1:
            self.index += 1
            self.overlay = [cv.imread('chat1.jpg'), cv.imread('chat2.jpg')]
        else:
            self.index = 0
            self.overlay = [cv.imread('chat1.jpg'), cv.imread('chat2.jpg')]

    # run video embedder
    def run(self, cameraimage):
        overlayimage = self.overlay[self.index]
        height, width, c = self.model.shape

        orb = cv.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(self.model, None) 

        overlayimage = cv.resize(overlayimage, (width, height))  # resize image to fit model image dimensions
        augmentedimage = cameraimage.copy()

        kp2, des2 = orb.detectAndCompute(cameraimage, None)
        matches = self.generateMatches(des1, des2)
        print(len(matches))

        if len(matches) > 250:
            return self.embed(cameraimage, overlayimage, kp1, kp2, matches, augmentedimage, height, width)
        return cameraimage

    # generates matches between two image descriptors
    # @param
    # des1: model image descriptors
    # des2: camera image descriptors
    def generateMatches(self, des1, des2):
        bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        return matches

    # does video embed in camera image
    # @param
    # cameraimage: cap.read() camera image
    # overlayimage: overlay image
    # kp1: model keypoints
    # kp2: camera image keypoints
    # matches: BFMatcher between model and camera image descriptors
    # augmentedimage: camera feed with video overlay
    # height: height of mask
    # width: width of mask
    def embed(self, cameraimage, overlayimage, kp1, kp2, matches, augmentedimage, height, width):
        srcpts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dstpts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        matrix, mask = cv.findHomography(srcpts, dstpts, cv.RANSAC, 5)

        points = np.float32([[0,0], [0,height], [width,height], [width,0]]).reshape(-1,1,2)
        dst = cv.perspectiveTransform(points, matrix)
        
        warpedimage = cv.warpPerspective(overlayimage, matrix, (cameraimage.shape[1], cameraimage.shape[0]))  # changes video frame shape into model surface

        newmask = np.zeros((cameraimage.shape[0], cameraimage.shape[1]), np.uint8)                        
        cv.fillPoly(newmask, [np.int32(dst)], (255, 255, 255))
        invertedmask = cv.bitwise_not(newmask)
        augmentedimage = cv.bitwise_and(augmentedimage, augmentedimage, mask=invertedmask)                  
        augmentedimage = cv.bitwise_or(warpedimage, augmentedimage)  
        return augmentedimage

    # @desc
    # handles timer events triggered by this class
    def timerEvent(self, event):
        if(event.timerId() != self.trigger.timerId()):
            print("timer shit fucked up")
            return

        augmentedimage = self.run()
        self.out_image.emit(augmentedimage)


# CALIBRATE USERNAME AND COLOR
class Setup(QWidget):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.color = [0,0,0]
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 140
        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.textbox = QLineEdit(self)
        self.textbox.move(20,20)
        self.textbox.resize(280,40)

        self.button = QPushButton('Color', self)
        self.button.move(20,80)
        self.button.clicked.connect(self.color_picker)

        self.button = QPushButton('Username', self)
        self.button.move(120,80)
        self.button.clicked.connect(self.on_click)

        self.styleChoice = QLabel("Color", self)

        self.show()

    def getUserName(self):
        return self.username

    def getRGB(self):
        return self.color

    def on_click(self):
        self.username = self.textbox.text()
        print(self.getUserName())

    def color_picker(self):
        color = QColorDialog.getColor()
        self.styleChoice.setStyleSheet("QWidget { background-color: %s}" % color.name())
        self.color = self.hex_to_rgb(color.name())

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

# @desc
# widget that instantiates all other widgets, sets layout, and connects signals to slots
class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("test UI window") #change name after testing
        self.windowTitleChanged.connect(lambda: self.alertWindowChanged()) # example of event-based flow for updating ui data

        self.display = DisplayWidget()
        self.video = TestVideo()
        self.imageoverlay = ImageOverlayCarousel()

        self.start_button = QPushButton('START')
        self.next_button = QPushButton('NEXT')
        self.carousel_button = QPushButton('CAROUSEL')

        self.video.image_data.connect(lambda x: self.display.setImage(x))
        self.start_button.clicked.connect(self.video.start)
        self.next_button.clicked.connect(self.video.next)
        self.carousel_button.clicked.connect(self.video.rotateCarousel)

        layout = QVBoxLayout()
        layout.addWidget(self.display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.carousel_button)

        self.setLayout(layout)

        """
        self.threadpool = QThreadPool()
        self.__create_worker(self.video.run)
        """

    def alertWindowChanged(self):
        print("ALERT")

    # @desc
    # handles double click event for all widgets in UI
    def mouseDoubleClickEvent(self, event):
        self.setWindowTitle("CHANGED")

    """
    def __create_worker(self, func):
        worker = JobRunner(func)
        self.threadpool.start(worker)
    """

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
    # someUI = UI()
    app = QApplication(sys.argv)
    ex = Setup()
    sys.exit(app.exec_())