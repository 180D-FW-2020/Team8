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
        'src/gui'
        'data/gui'
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

# implementations with out modules
import mqtt as mqtt 
import speech as speech
import chat as chat 
import animations as animations


DRESW = 1280 # resolution width
DRESH = 720 # res height
DFORMAT = QImage.Format_RGB888 # color space
DSCALE = 2 # display scaling factor
DRATE = 30 # frames per second
DINTERVAL = round(1000/DRATE) # frame refresh interval (msec)
TOPICS = ["Nate", "Tommy", "Michael", "Nico"]
PHRASES = ["place", "message", "return", "cancel"] 

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
    yesSignal = pyqtSignal()
    noSignal = pyqtSignal()
    placeSignal = pyqtSignal()
    cancelSignal = pyqtSignal()
    returnSignal = pyqtSignal()
    messageSignal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.signals = [self.placeSignal, self.messageSignal, self.returnSignal, self.cancelSignal]
        self.phrases = {PHRASES[i] : self.signals[i] for i,_ in enumerate(PHRASES)}
        self.homographyIsActive = False

        self.timer = QTimer(self)

        self.display = DisplayWidget()
        self.video = ThreadVideo()
        self.manager = chat.BoardManager(user='Nico')
        self.overlay = chat.BoardOverlay()
        self.emote = animations.EmoteWidget()
        self.listener = speech.AudioObject({PHRASES[i]:False for i, _ in enumerate(PHRASES)})
        self.setMainLayout()

        self.signals = self.signals.append(self.listener.transcribed_phrase)
        self.slots = [self.toggleHomography, self.messageListenSlot]

        self.listener.transcribed_phrase.connect(lambda message:self.manager.userPost(message))

        # create all relevant chats
        for topic in TOPICS:
            self.manager.createBoard(topic)

        self.__constant_workers__()
        self.__internal_connect__()

        # signal creation for states with keyphrases
        for state, phrases in states_with_phrases.items():
            self._setStatePhrases(state, phrases)

        self.fsm = FSM()

    def __internal_connect__(self):
        # manager -> overlay
        self.manager.topic.connect(lambda topic: self.overlay.changeTopic(topic))

        # display
        for board in BoardManager.boards.values():
            board["net"].emoji.connect(lambda emotes: self.emote.spawn_emotes(emotes))

        self.fsm(self.signals, self.slots)
        
        

    def __create_worker__(self, func):
        worker = JobRunner(func)
        self.threadpool.start(worker)

    def __constant_workers__(self):
        self.__create_worker__(self.video.captureFrames)
        self.timer.start(DINTERVAL)

        self.__create_worker__(self.listener.speechHandler)
        self.__create_worker__(self.listener.receivePhrase)
        for board in BoardManager.boards.values():
            self.__create_worker__(board["net"].listen)

    def __phrase_rec__(self, phrase):
        if phrase in PHRASES:
            self.phrases[phrase].emit()

    def __imgpass__(self, imqueue):
        if not imqueue.empty():
            img = imqueue.get()
            if img is not None and len(img) > 0:
                if self.homographyIsActive:
                    self.frame_data.emit(self.overlay.run(img))
                else:
                    self.frame_data.emit(img)

    def __print_state__(self, state, sID):
        state.entered.connect(lambda: print("current state: " + str(sID)))

    def __print_phrases__(self):
        while(1):
            time.sleep(1)
            print(self.audio_recognizer.phrases)

    def toggleHomography(self):
        self.homographyIsActive = not self.homographyIsActive

    # NOTE: replace message slots with textwidget functions or smth if desired
    def messageListenSlot(self):
        self.listener.resetCurrentPhrase()
        self.listener.sendCurrentPhrase()

    def setMainLayout(self):
        self.layout.addWidget(self.display, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.emote, 0, 0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)