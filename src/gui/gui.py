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
        '../img_implanter/mqtt_comms',
        '../envrd/audio',
        # '../envrd/gesture_detector',
        # '../env_reader/image_tracking/hand_tracker'
       ]

import sys

for lib in PATH:
    sys.path.append(lib)

import time
# from os import path
import cv2 as cv
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading
# import IMU
import message_placer as placer
import mqtt_link as mqtt
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

## MQTT QObject Class #######################################################################################################
class MQTTNetObject(QObject, mqtt.MQTTLink):
    new_message = pyqtSignal(str)
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def receiveMessage(self, message):
        form_message = message['sender'] + ": " + message['data']
        self.new_message.emit(form_message)
        
    def sendMessage(self, message, receiver, sender):
        self.addText(message, receiver, sender)
        self.send()

class AudioObject(QObject):
    detected_phrase = pyqtSignal(str)
    transcribed_phrase = pyqtSignal(str)
    def __init__(self, keyphrases : dict, parent=None):
        super().__init__(parent)
        self.recognizer = audio.SpeechRecognizer(keyphrases)

    # @desc
    # emits a string containing the most recently transcribed phrase
    def sendCurrentPhrase(self):
        s = self.recognizer.current_phrase
        if s != None:
            self.transcribed_phrase.emit(s)
        else:
            print("error: current phrase is null")

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
                        # self.recognizer.teardown()
                    # end = True
        except TypeError:
            pass
        except ValueError:
            pass

    def speechHandler(self):
        # self.timer.start(ATIMEOUT)
        self.recognizer.listenForPhrases()
        self.recordDetection()

class MessageBoard(QWidget):
    board_image = pyqtSignal(np.ndarray)
    def __init__(self, username, num_messages=5, parent=None):
        super().__init__(parent)
        # get an MQTT link
        self.messenger = MQTTNetObject(board="ece180d/MEAT/general")
        self.placer = placer.MessagePlacer("br", num_messages)

        # get a username
        self.username = 'dft_username'

        # set up message reading
        self.num_messages = num_messages
        self.messages = []

        # update message list upon new message
        self.messenger.new_message.connect(lambda message: self.__update_messages(message))

    def __update_messages(self, new_message):
        # append messages so that the last message printed is at bottom
        self.messages.append(new_message)
        print(self.messages)

        # cut it off at 5
        if len(self.messages) > self.num_messages:
            del self.messages[0]

    def placeBoard(self, frame):
        frame = self.placer.placeMessages(self.messages, frame)
        frame = self.placer.placeUserMessage(self.username + ": ", frame)
        self.board_image.emit(frame)

    def receive(self):
        self.messenger.listen()
    
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
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, DRESW)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, DRESH)
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
    yesSignal = pyqtSignal()
    noSignal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        # widgets and objects
        self.display = DisplayWidget()
        self.board = MessageBoard('default_username')
        self.start_button = QPushButton('START')
        self.video = TestVideo()
        self.audio_phrases = {}
        self.audio_recognizer = AudioObject(self.audio_phrases)
        self.layout = QVBoxLayout()
        self.setMainLayout()

        # state machine
        self.state_machine = QStateMachine()


        self.s_start = QState()
        
        self.s_cal = QState()
        self.s_cal_ht = QState(self.s_cal)
        self.s_cal_wave = QState(self.s_cal)
        self.s_cal_fin = QFinalState(self.s_cal)
        self.s_cal.setInitialState(self.s_cal_ht)

        self.s_main = QState(childMode=1) # parallel child states

        self.s_img = QState(self.s_main)
        self.s_img_init = QState(self.s_img)
        self.s_img_find = QState(self.s_img)
        self.s_img_confirm = QState(self.s_img)
        self.s_img_display = QState(self.s_img)
        self.s_img.setInitialState(self.s_img_init)

        self.s_msg = QState(self.s_main)
        self.s_msg_init = QState(self.s_msg)
        self.s_msg_listen = QState(self.s_msg)
        self.s_msg_confirm = QState(self.s_msg)
        self.s_msg_send = QState(self.s_msg)
        self.s_msg.setInitialState(self.s_msg_init)

        # state signals
        # TODO; need module objects to set up more signals/slots
            
        # signal creation for states with keyphrases
        states_with_phrases = {
                                self.s_cal_ht : 'okay',
                                self.s_img_init : 'place',
                                self.s_img_display : 'next',
                                self.s_img_confirm : 'yes',
                                self.s_img_confirm : 'no',
                                self.s_msg_init : 'message',
                                self.s_msg_confirm : 'yes',
                                self.s_msg_confirm : 'no'
                            }
        for state, phrase in states_with_phrases.items():
            self._setStatePhrase(state, phrase)

        self.s_start.addTransition(self.start_button.clicked, self.s_cal)
        self.calibrationStateHandler()
        self.messageStateHandler()
        self.imageStateHandler()

        # signals and slots
        self.video.image_data.connect(lambda x: self.display.setImage(x))
        self.start_button.clicked.connect(self.video.start)
        self.start_button.clicked.connect(lambda: self.deleteWidget(self.start_button))
        self.audio_recognizer.detected_phrase.connect(lambda x: self.display.keyphrasehandler(x))

        # state machine init
        self.state_machine.addState(self.s_start)
        self.state_machine.addState(self.s_cal)
        self.state_machine.addState(self.s_main)
        self.state_machine.setInitialState(self.s_start)
        self.state_machine.start()

        # threading
        self.threadpool = QThreadPool()

    def calibrationStateHandler(self):
        self.s_cal.entered.connect(lambda: self.__create_worker(self.audio_recognizer.speechHandler))
        # self.s_cal_ht.addTransition(SOMESIG, self.s_cal_wave)
        # self.s_cal_wave.addTransition(SOMESIG, self.s_cal_fin)
        self.s_cal.addTransition(self.s_cal.finished, self.s_main)

    def messageStateHandler(self):
        self.s_msg_init.addTransition(self.audio_recognizer.detected_phrase, self.s_msg_listen)
        self.s_msg_listen.entered.connect(self.messageListenSlot)
        self.s_msg_listen.addTransition(self.audio_recognizer.transcribed_phrase, self.s_msg_confirm)
        # self.s_msg_confirm.entered.connect('''ask user to confirm, and print transcribed phrase''')
        msg_confirm_handler = lambda x: self.confirmSlot(x)
        self._phraseOptionHandler(self.s_msg_confirm, msg_confirm_handler)
        self.s_msg_confirm.addTransition(self.yesSignal, self.s_msg_send)
        self.s_msg_confirm.addTransition(self.noSignal, self.s_msg_listen)
        # self.s_msg_send.addTransition(someMQTTsignal, self.s_msg_init)

    def imageStateHandler(self):
        self.s_img_init.addTransition(self.audio_recognizer.detected_phrase, self.s_img_find)
        # self.s_img_find.addTransition(someFlatSurfacesignal, self.s_img_confirm)
        img_confirm_handler = lambda x: self.confirmSlot(x)
        self._phraseOptionHandler(self.s_img_confirm, img_confirm_handler)
        self.s_img_confirm.addTransition(self.yesSignal, self.s_img_display)
        self.s_img_confirm.addTransition(self.noSignal, self.s_img_init)
        # self.audio_recognizer.detected_phrase.connect(someHomographyProcess during s_img_display)

    # NOTE: replace message slots with textwidget functions or smth if desired
    def messageListenSlot(self):
        self.audio_recognizer.recognizer.resetCurrentPhrase()
        time.sleep(5)
        self.audio_recognizer.sendCurrentPhrase()

    # NOTE: replace message slots with textwidget functions or smth if desired
    def confirmSlot(self, ans):
        if ans == 'yes':
            self.yesSignal.emit()
        elif ans == 'no':
            self.noSignal.emit()
        else:
            print("error: received phrase is not `yes` nor `no`")

    def setMainLayout(self):
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.start_button)
        self.setLayout(self.layout)

        self.threadpool = QThreadPool()

        self.__create_worker(self.board.receive)

    def __create_worker(self, func):
        worker = JobRunner(func)
        self.threadpool.start(worker)

    def deleteWidget(self, widget):
        self.layout.removeWidget(widget)
        widget.deleteLater()
        widget = None

    # @desc
    # takes a state and a handler function for any detected phrase for that state.
    # sets up and tears down connection to the handler during the state's existence
    def _phraseOptionHandler(self, state, handler):
        h = handler
        confirm_handle = lambda: self.audio_recognizer.detected_phrase.connect(h)
        state.entered.connect(confirm_handle)
        confirm_teardown = lambda: self.audio_recognizer.detected_phrase.disconnect(h)
        state.exited.connect(confirm_teardown)

    # @desc
    # adds and removes keyphrases for audio recog's hotphrase list during a state's existence
    def _setStatePhrase(self, state, phrase):
        add_phrase = lambda: self.audio_recognizer.recognizer.addKeyphrase(phrase)
        rm_phrase = lambda: self.audio_recognizer.recognizer.removeKeyphrase(phrase)
        state.entered.connect(add_phrase)
        state.exited.connect(rm_phrase)

    def __create_worker(self, func):
        worker = JobRunner(func)
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
