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
        '../comms/mqtt',
        '../envrd',
        '../imgproc',
        '../../data/gui'
       ]

import sys

for lib in PATH:
    sys.path.append(lib)

import time
try:
    import Queue
except:
    import queue as Queue
import cv2 as cv
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import message_placer as placer
import hand_tracker.hand_tracker as hand_tracker

# implementations with out modules
import mqtt 
import speech


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
class JobSignals(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
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
            return
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.output.emit(output)
        finally:
            self.signals.done.emit()

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

# @ desc
# threadbale video class for reading frames from camera capture.
# places frames into 2-frame buffer queue, from which the main widget reads/emits to modules
class ThreadVideo(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv.VideoCapture(0)
        # self.cap.set(cv.CAP_PROP_FRAME_WIDTH, DRESW)
        # self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, DRESH)
        # self.cap.set(cv.CAP_PROP_FPS, 30)
        self.buffer = Queue.Queue()

    def capture_frames(self):
        while(1):
            read, frame = self.cap.read()
            if read:
                if frame is not None and self.buffer.qsize() < 2:
                    self.buffer.put(frame)
                else:
                    time.sleep(DINTERVAL/1000.0)
            else:
                print("unable to grab image") 

# @desc
# class for opencv image carousel using ar overlay
class ImageOverlayCarousel(QObject):
    out_image = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = cv.imread('../../data/gui/model_qr.png')
        self.overlay = [cv.imread('../../data/gui/sample1.jpg'), cv.imread('../../data/gui/sample2.jpg')]
        # self.trigger = QBasicTimer()
        self.counter = 0
        self.index = 0

    # @desc
    # event trigger for an instantaneous event; use when an event overload is not desired
    # or when an event trigger must cause a custom signal to emit
    # def start(self):
    #     self.trigger.start(0, self)

    def next(self):
        if self.index != len(self.overlay) - 1:
            self.index += 1
        else:
            self.index = 0

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
        # print(len(matches))

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
    # def timerEvent(self, event):
    #     if(event.timerId() != self.trigger.timerId()):
    #         print("timer shit fucked up")
    #         return

    #     augmentedimage = self.run()
    #     self.out_image.emit(augmentedimage)

# @desc
# widget that instantiates all other widgets, sets layout, and connects signals to slots
# also handles threading
class MainWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.display = DisplayWidget()
        self.video = ThreadVideo()
        self.manager = BoardManager(user='Nico')
        self.audio_phrases = {}
        self.listener = AudioObject(self.audio_phrases)
        self.setMainLayout()

        # signal creation for states with keyphrases
        states_with_phrases = {
                                self.s_cal_ht : ['okay'],
                                self.s_img_init : ['place'],
                                self.s_msg_init : ['message'],
                                self.s_msg_confirm : ['yes', 'no']
                            }
        for state, phrases in states_with_phrases.items():
            self._setStatePhrases(state, phrases)

        self.sm = BoardFSM()