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
        '../env_reader/image_tracking/hand_tracker'
       ]

import sys

for lib in PATH:
    sys.path.append(lib)

import time
try:
    import Queue
except:
    import queue as Queue
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
import hand_tracker
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
    pass
    # error = pyqtSignal(tuple) # redirect error reporting
    # output = pyqtSignal(object) # notify slot of function returned value
    # done = pyqtSignal() # notify main thread of completion

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
            # traceback.print_exc()
            # exctype, value = sys.exc_info()[:2]
            # self.signals.error.emit((exctype, value, traceback.format_exc()))
        # else:
            # self.signals.output.emit(output)
        # finally:
        #     self.signals.done.emit()

## MQTT QObject Class #######################################################################################################
## QObject connector for MQTT stuff
class MQTTNetObject(QObject, mqtt.MQTTLink):
    new_message = pyqtSignal(str)
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def receiveMessage(self, message):
        form_message = message['sender'] + ": " + message['data']
        self.new_message.emit(form_message)
        
    def sendMessage(self, message, sender):
        self.addText(message, sender)
        self.send()

class AudioObject(QObject, audio.SpeechRecognizer):
    detected_phrase = pyqtSignal(str)
    transcribed_phrase = pyqtSignal(str)
    error = pyqtSignal()
    def __init__(self, keyphrases : dict, *args, parent=None, **kwargs):
        super().__init__(parent, keyphrases=keyphrases)

    # @desc
    # emits a string containing the most recently transcribed phrase
    def sendCurrentPhrase(self):
        s = self.current_phrase
        if s != None:
            self.transcribed_phrase.emit(s)
            return
        else:
            time.sleep(1)
            self.sendCurrentPhrase()

    def receivePhrase(self):
        try:
            for phrase, found in self.phrases.items():
                if found == True:
                    self.resetDetection(phrase)
                    self.detected_phrase.emit(phrase)
        except TypeError:
            pass
        except ValueError:
            pass


    # @desc
    # waits for a keyphrase to be found, then returns the first detected phrase
    # def recordDetection(self):
    #     end = False
    #     try:
    #         while(end == False):
    #             for phrase, found in self.recognizer.phrases.items():
    #                 if found == True:
    #                     self.recognizer.resetDetection(phrase)
    #                     self.detected_phrase.emit(phrase)
    #                     # self.recognizer.teardown()
    #                     # end = True
    #     except TypeError:
    #         pass
    #     except ValueError:
    #         pass

    def speechHandler(self):
        # self.timer.start(ATIMEOUT)
        self.listenForPhrases()
        # self.recordDetection()

## Message Board Class #######################################################################################################
## takes in data from a general MQTT board and places it in UI, also takes in user input to send messages
class MessageBoard(QWidget):
    board_image = pyqtSignal(np.ndarray)
    def __init__(self, username='xxxx', num_lines=5, parent=None):
        super().__init__(parent)
        # get an MQTT link
        self.messenger = MQTTNetObject(board="ece180d/MEAT/general")
        self.board_shape = (200, 200)
        self.placer = placer.BoardPlacer(self.board_shape, "br", num_lines)

        # set up message reading
        self.num_lines = num_lines
        self.user_message = {"username":username, "message":"", "state_phrase":""}

        # update message list upon new message
        self.messenger.new_message.connect(lambda message: self.__update_messages(message))

    def __update_messages(self, new_message):
        # append messages so that the last message printed is at bottom
        self.placer.updateChatBoard(new_message)

    def listenUserMessage(self):
        self.user_message["state_phrase"] = "      Listening..."
        self.placer.updateUserBoard(self.user_message.values())

    def confirmUserMessage(self, message):
        self.user_message["message"] = message
        self.user_message["state_phrase"] = "      Send?"
        self.placer.updateUserBoard(self.user_message.values())

    def sendUserMessage(self):
        self.messenger.sendMessage(self.user_message["message"], self.user_message["username"])

    def placeBoard(self, frame):
        frame = self.placer.placeBoard(frame)
        self.board_image.emit(frame)

    def receive(self):
        self.messenger.listen()

class IMUBoard(QWidget):
    # CONSOLIDATE WITH MESSAGEBOARD - REFACTOR
    board_image = pyqtSignal(np.ndarray)
    def __init__(self, num_lines=2, parent=None):
        super().__init__(parent)
        # get an MQTT link
        self.messenger = MQTTNetObject(board="ece180d/MEAT/imu")
        self.board_shape = (40, 400)
        self.placer = placer.BoardPlacer(self.board_shape, "tl", num_lines)

        # set up message reading
        self.num_lines = num_lines

        # update message list upon new message
        self.messenger.new_message.connect(lambda message: self.__update_messages(message))

    def __update_messages(self, new_message):
        # append messages so that the last message printed is at bottom
        self.placer.updateChatBoard(new_message)

    def placeBoard(self, frame):
        frame = self.placer.placeBoard(frame)
        self.board_image.emit(frame)    
    
    def receive(self):
        self.messenger.listen()

## Hand Tracker QObject Class #######################################################################################################
## tracks hand in UI by placing box where it sees the hand
class HandTracker(QObject):
    hand_image = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracker = hand_tracker.hand_tracker((160, 200, 200), (120, 100, 50), [0.5, 0.25, 0.25], debug=False) # values for upper_HSV, lower_HSV, can be changed

    def findHand(self, frame):
        frame, loc = self.tracker.locAdder(frame)
        self.hand_image.emit(frame)
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
        # self.cap.set(cv.CAP_PROP_FRAME_WIDTH, DRESW)
        # self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, DRESH)
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
            print("error: timer ID mismatch")
            return
            
        read, frame = self.cap.read()
        if read:
            self.image_data.emit(frame)

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
        self.model = cv.imread('model2.png')
        self.overlay = [cv.imread('sample1.jpg'), cv.imread('sample2.jpg')]
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
        print(len(matches))

        if len(matches) > 200:
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

# @desc
# widget that instantiates all other widgets, sets layout, and connects signals to slots
# also handles threading
class MainWidget(QWidget):
    yesSignal = pyqtSignal()
    noSignal = pyqtSignal()
    msgEntry = pyqtSignal()
    imgEntry = pyqtSignal()
    frame_data = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)

        # widgets and objects
        self.display = DisplayWidget()
        self.text_board = MessageBoard('default_username')
        self.imu_board = IMUBoard()
        self.start_button = QPushButton('START')
        self.tracker = HandTracker()
        # self.video = TestVideo()
        self.video = ThreadVideo()
        self.frame_timer = QTimer(self)
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
        ## connections to main
        self.s_main.entered.connect(self.__mqtt_thread)                                           # start mqtt when main window starts

        # put states into a dict and create IDs for them
        states_and_IDs = {
                            self.s_start : 0,
                            self.s_cal: 10,
                            self.s_cal_ht: 11,
                            self.s_cal_wave: 12,
                            self.s_cal_fin: 13,
                            self.s_main: 20,
                            self.s_img: 30,
                            self.s_img_init: 31,
                            self.s_img_find: 32,
                            self.s_img_confirm: 33,
                            self.s_img_display: 34,
                            self.s_msg: 40,
                            self.s_msg_init: 41,
                            self.s_msg_listen: 42,
                            self.s_msg_confirm: 43,
                            self.s_msg_send: 44
                        }
        for state, sID in states_and_IDs.items():
            self._print_current_state(state, sID)

        # signal creation for states with keyphrases
        states_with_phrases = {
                                self.s_cal_ht : ['okay'],
                                self.s_img_init : ['place'],
                                self.s_img_display : ['next'],
                                self.s_img_confirm : ['yes', 'no'],
                                self.s_msg_init : ['message'],
                                self.s_msg_confirm : ['yes', 'no']
                            }
        for state, phrases in states_with_phrases.items():
            self._setStatePhrases(state, phrases)

        self.s_start.addTransition(self.start_button.clicked, self.s_main)
        self.calibrationStateHandler()
        self.messageStateHandler()
        self.imageStateHandler()

        # signals and slots
        # self.video.image_data.connect(lambda x: self.text_board.placeBoard(x)) # image_data is handed to the board first
        self.frame_data.connect(lambda x: self.text_board.placeBoard(x)) 
        self.audio_recognizer.transcribed_phrase.connect(lambda x: self.text_board.confirmUserMessage(x)) # when a phrase is transcribed, board gets it

        # self.text_board.board_image.connect(lambda x: self.display.setImage(x))
        self.text_board.board_image.connect(lambda x:self.imu_board.placeBoard(x))
        self.imu_board.board_image.connect(lambda x:self.tracker.findHand(x))
        self.tracker.hand_image.connect(lambda x:self.display.setImage(x))
        # self.start_button.clicked.connect(self.video.start)
        self.frame_timer.timeout.connect(lambda: self._pass_image(self.video.buffer))
        self.start_button.clicked.connect(self._start_video)
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

        # self.__create_worker(self._print_phrases)

    def _start_video(self):
        print("starting video...")
        self.frame_timer.start(DINTERVAL)
        self.__create_worker(self.video.capture_frames)

    def _pass_image(self, imqueue):
        if not imqueue.empty():
            img = imqueue.get()
            if img is not None and len(img) > 0:
                # print("emitting frame")
                self.frame_data.emit(img)

    def _print_current_state(self, state, sID):
        state.entered.connect(lambda: print("current state: " + str(sID)))

    def _print_phrases(self):
        while(1):
            time.sleep(1)
            print(self.audio_recognizer.phrases)

    def calibrationStateHandler(self):
        self.s_main.entered.connect(lambda: self.__create_worker(self.audio_recognizer.speechHandler))
        # self.s_cal_ht.addTransition(SOMESIG, self.s_cal_wave)
        # self.s_cal_wave.addTransition(SOMESIG, self.s_cal_fin)
        self.s_cal.addTransition(self.s_cal.finished, self.s_main)

    def messageStateHandler(self):
        # transition when message is heard
        msg_init_handler = lambda x: self.initSlot(x)
        self._phraseOptionHandler(self.s_msg_init, msg_init_handler)
        self.s_msg_init.addTransition(self.msgEntry, self.s_msg_listen)

        # when state is entered, listen for 5 seconds
        self.s_msg_listen.entered.connect(self.messageListenSlot)
        
        # then, at end fo 5 seconds, transition to confirming the message
        self.s_msg_listen.addTransition(self.audio_recognizer.transcribed_phrase, self.s_msg_confirm)
        self.s_msg_listen.entered.connect(self.text_board.listenUserMessage)

        msg_confirm_handler = lambda x: self.confirmSlot(x)
        self._phraseOptionHandler(self.s_msg_confirm, msg_confirm_handler)      ## connections to msg

        # transition to sending message if message is confirmed
        self.s_msg_confirm.addTransition(self.yesSignal, self.s_msg_send)

        # send back to init state
        self.s_msg_send.entered.connect(self.text_board.sendUserMessage)
        self.s_msg_send.addTransition(self.s_msg_send.entered, self.s_msg_init)

        # transition back to listening if user doesn't like message
        self.s_msg_confirm.addTransition(self.noSignal, self.s_msg_listen)
        # self.s_msg_send.addTransition(someMQTTsignal, self.s_msg_init)

        # TODO: add transition from s_msg_send to s_msg_init

    def imageStateHandler(self):
        img_init_handler = lambda x: self.initSlot(x)
        self._phraseOptionHandler(self.s_img_init, img_init_handler)
        self.s_img_init.addTransition(self.imgEntry, self.s_img_find)
        # self.s_img_find.addTransition(someFlatSurfacesignal, self.s_img_confirm)
        img_confirm_handler = lambda x: self.confirmSlot(x)
        self._phraseOptionHandler(self.s_img_confirm, img_confirm_handler)
        self.s_img_confirm.addTransition(self.yesSignal, self.s_img_display)
        self.s_img_confirm.addTransition(self.noSignal, self.s_img_init)
        # self.audio_recognizer.detected_phrase.connect(someHomographyProcess during s_img_display)

    # NOTE: replace message slots with textwidget functions or smth if desired
    def messageListenSlot(self):
        self.audio_recognizer.resetCurrentPhrase()
        self.__create_worker(self.audio_recognizer.sendCurrentPhrase())

    # NOTE: replace message slots with textwidget functions or smth if desired
    def confirmSlot(self, ans):
        # print("entered confirm slot")
        if ans == 'yes':
            self.yesSignal.emit()
        elif ans == 'no':
            self.noSignal.emit()
        else:
            print("error: received phrase is not `yes` nor `no`")

    def initSlot(self, ans):
        if ans == 'message':
            self.msgEntry.emit()
        elif ans == 'place':
            self.imgEntry.emit()

    def setMainLayout(self):
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.start_button)
        self.setLayout(self.layout)

    def __create_worker(self, func):
        worker = JobRunner(func)
        self.threadpool.start(worker)

    def __mqtt_thread(self):
        self.__create_worker(self.text_board.receive)
        self.__create_worker(self.imu_board.receive)

    def deleteWidget(self, widget):
        self.layout.removeWidget(widget)
        widget.deleteLater()
        widget = None

    # @desc
    # takes a state and a handler function for any detected phrase for that state.
    # sets up and tears down connection to the handler during the state's existence
    def _phraseOptionHandler(self, state, handler):
        # when a new state is entered, connect the detect_phrase signal in the audio recognizer to the handler
        confirm_handle = lambda: self.audio_recognizer.detected_phrase.connect(handler)
        state.entered.connect(confirm_handle)

        # when that state is exited, this is removed
        confirm_teardown = lambda: self.audio_recognizer.detected_phrase.disconnect(handler)
        state.exited.connect(confirm_teardown)

    # @desc
    # adds and removes keyphrases for audio recog's hotphrase list during a state's existence
    def _setStatePhrases(self, state, phrases):
        for phrase in phrases:
            add_phrase = lambda val=phrase: self.audio_recognizer.addKeyphrase(val)
            rm_phrase = lambda val=phrase: self.audio_recognizer.removeKeyphrase(val)
            state.entered.connect(add_phrase)
            state.exited.connect(rm_phrase)

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
