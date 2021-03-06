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
        'src/comms/mqtt',
        'src/envrd',
        'src/imgproc',
        'src/gui',
        'data/gui',
        'data'
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
# import data.resources
# implementations with out modules
import resources
import net
import mqtt 
import speech 
import chat
import animations 
import calibrate

from fsm import *

DRESW = 640 # resolution width
DRESH = 480 # res height
DFORMAT = QImage.Format_RGB888 # color space
DSCALE = 2 # display scaling factor
DRATE = 30 # frames per second
DINTERVAL = round(1000/DRATE) # frame refresh interval (msec)
PHRASES = ["place", "message", "return", "cancel", "yes", "no"] 

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
        self.image = self.image.scaled(int(DRESW*0.75), int(DRESH*0.75), Qt.KeepAspectRatio, Qt.SmoothTransformation)
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

    def captureFrames(self):
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
# widget that instantiates all other widgets, sets layout, and connects signals to slots
# also handles threading
class MainWidget(QWidget):
    frameSignal = pyqtSignal(np.ndarray)
    yesSignal = pyqtSignal()
    noSignal = pyqtSignal()
    placeSignal = pyqtSignal()
    cancelSignal = pyqtSignal()
    returnSignal = pyqtSignal()
    messageSignal = pyqtSignal()
    
    def __init__(self, screensize, parent=None):
        super().__init__(parent)
        global DRESW,DRESH
        DRESW,DRESH = screensize

        # MainWidget Object Members
        self.timer = QTimer(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setup = calibrate.Setup()
        self.setup.init()

        self.display = DisplayWidget()
        self.video = ThreadVideo()
        self.manager = chat.BoardManager(user='default')
        self.overlay = chat.BoardOverlay()
        self.emote = animations.EmoteWidget()
        self.listener = speech.AudioObject({PHRASES[i]:False for i, _ in enumerate(PHRASES)})
        self.gesturer = net.MQTTIMUObject(user='default')

        self.layout = QGridLayout()
        self.threadpool = QThreadPool()

        # set up signals to pass to fsm
        self.signals = [
            self.placeSignal, 
            self.messageSignal, 
            self.returnSignal, 
            self.cancelSignal, 
            self.yesSignal, 
            self.noSignal,
            self.listener.transcribed_phrase
            ]

        # set up slots to pass to fsm
        yesHomo = lambda: self.setHomography(True)
        noHomo = lambda: self.setHomography(False)

        self.slots = [
            yesHomo, 
            noHomo, 
            self.messageListenSlot, 
            self.manager.send
            ]

        # instantiate fsm
        self.fsm = FSM(self.signals, self.slots)

        self.phrases = {PHRASES[i] : self.signals[i] for i,_ in enumerate(PHRASES)}
        self.homographyIsActive = True

        self.__constant_workers__()
        self.__internal_connect__()

    def __run__(self):
        self.setMainLayout()
        
        self.manager.setColor(self.setup.getRGB())
        self.manager.setUser(self.setup.getUserName())
        self.__create_chatrooms__(self.setup.getChatrooms())

        self.setup.hide()
        self.fsm.state_machine.start()

    def __create_chatrooms__(self, chatrooms):
        # create all relevant chats
        for chat in chatrooms:
            self.manager.createBoard(chat)

    def __internal_connect__(self):
        self.gesturer.gestup.connect(lambda up: self.manager.switchTopic(up))

        # connect calibration to rest of system
        self.setup.nextSignal.connect(self.__run__)

        # manager connections
        self.manager.switch.connect(lambda topic: self.overlay.changeTopic(topic))
        self.manager.emoji.connect(lambda emojis: self.emote.spawn_emotes(emojis))

        # listener connections (not in FSM)
        self.listener.transcribed_phrase.connect(lambda message:self.manager.stage(message))
        self.listener.detected_phrase.connect(lambda phrase:self.__phrase_rec__(phrase))

        # timeout and framing connections
        self.timer.timeout.connect(lambda: self.__imgpass__(self.video.buffer))
        self.frameSignal.connect(lambda image: self.display.setImage(image))


    def __create_worker__(self, func, *args, **kwargs):
        worker = JobRunner(func, *args, **kwargs)
        self.threadpool.start(worker)

    def __constant_workers__(self):
        self.timer.start(DINTERVAL)
        self.__create_worker__(self.manager.sendConstant)       # constantly sends out info
        self.__create_worker__(self.video.captureFrames)        # constantly captures frames
        self.__create_worker__(self.listener.speechHandler)     # constantly listens
        self.__create_worker__(self.manager.link.listen)        # constantly mqtt listening
        self.__create_worker__(self.__print_phrases__)          # constantly printing PHRASES
        self.__create_worker__(self.gesturer.link.listen)       # constantly mqtt listening (gesturer)

    def __phrase_rec__(self, phrase):
        if phrase in PHRASES:
            self.phrases[phrase].emit()

    def __imgpass__(self, imqueue):
        if not imqueue.empty():
            img = imqueue.get()
            if img is not None and len(img) > 0:
                if self.homographyIsActive:
                    self.frameSignal.emit(self.overlay.run(img))
                else:
                    self.frameSignal.emit(img)

    def __print_phrases__(self):
        while(1):
            time.sleep(1)
            print(self.listener.phrases)

    def setHomography(self, value):
        self.homographyIsActive = value

    # for testing purposes
    def keyPressEvent(self, event):
        super(MainWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_P:
            self.placeSignal.emit()
        if event.key() == Qt.Key_R:
            self.returnSignal.emit()
        if event.key() == Qt.Key_M:
            self.messageSignal.emit()
        if event.key() == Qt.Key_C:
            self.cancelSignal.emit()
        if event.key() == Qt.Key_Y:
            self.yesSignal.emit()
        if event.key() == Qt.Key_N:
            self.noSignal.emit()
        if event.key() == Qt.Key_S:
            self.gesturer.gestup.emit(True)

    # NOTE: replace message slots with textwidget functions or smth if desired
    # NOTE: all slots should create workers for functions needing threading

    def messageListenSlot(self):
        self.listener.resetCurrentPhrase()
        self.__create_worker__(self.listener.sendCurrentPhrase)

    def setMainLayout(self):
        self.layout.addWidget(self.display, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.emote, 0, 0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
