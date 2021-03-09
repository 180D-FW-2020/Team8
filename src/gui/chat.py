import sys

PATH = [
    "src/gui",
    "src/tools",
    "test"
]

for lib in PATH:
    sys.path.append(lib)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import cv2 as cv

import mqtt_net as mqtt
import archat
import numpy as np
import time as t
from datetime import datetime as time
import stringparser

## Globals #######################################################################################################
## a list of globals used in this file

DELIM = "slash"
TOPICPREF = "ece180d/MEAT/"
ROOT = "data/gui/"
EMOTEIDS = {
    "angry"        : 1 ,
    "cringe"       : 2 ,
    "cry"          : 3 ,
    "doubt"        : 4 ,
    "LOL"          : 5 ,
    "welp"         : 6 ,
    "frown"        : 7 ,
    "grin"         : 8 ,
    "love"         : 9 ,
    "ofcourse"     : 10,           
    "shock"        : 11,
    "simp"         : 12,
    "smile"        : 13,
    "hmmm"         : 14,
    "tongue"       : 15,
    "wink"         : 16        
            }
MSG = {
            "message_type" : str,
            "sender" : str,
            "data" : str,
            "time" : {
                "hour": int,
                "minute": int,
                "second": int
            },
            "ID" : int, 
            "color": tuple, 
            "emoji": list
        }
EMPTYBOARD = {  
    "topic"     :
    {"link"      :   mqtt.MQTTLink, 
    "chat"      :   archat.ARChat}
            }

## BoardManager #######################################################################################################
## a class for managing all of the ARChat boards

class BoardManager(QObject):
    '''
    A BoardManager object manages the handshake between each ARChat object and each MQTTLink object

    Public Members:
        - switch: a PyQt signal emitted whenever a board is switched to a new topic
        - user: a string containing user's username
        - color: an RGB tuple containing the user's color
        - topic: the current topic that the manager is writing to
        - boards: a list of boards to which the manager is subscribed

    Public Functions: 
        - createBoard: creates a new board which posts to topic
        - switchTopic: switches the topic to either the next or previous
        - send: sends a message to the currently active board
        - listen: activates listening of all currently active boards
    '''
    switch = pyqtSignal(str)
    emoji = pyqtSignal(list)
    def __init__(self, user, color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)), parent=None):
        super().__init__(parent)
 
        self.user = user
        self.color = color
        self.text = ""
        self.board = "general"
        self.link = mqtt.MQTTLink(topic='ece180d/MEAT', user_id=user, color=color)
        self.chats = {}

        self.createBoard(self.board)
        self.stage(' ')

        self.link.message.connect(lambda message: self.__receive__(message))

    def __time__(self):
        now = time.now()
        return { "hour": now.hour, "minute": now.minute, "second": now.second }

    def __receive__(self, datapacket):
        board = datapacket['board']
        try:
            chat = self.chats[board]
        except KeyError:
            print("Whoa! Looks like there isn't a board with that topic.")
        
        user, color, time, text, emojis = datapacket['sender'], datapacket['color'], datapacket['time'], datapacket['data'], datapacket['emoji']

        chat.post(user, text, color, time)
        self.emoji.emit(emojis)

    def __parse__(self, message):
        text, emojis = stringparser.parse_string(message, DELIM, EMOTEIDS)
        return text, emojis

    def createBoard(self, board:str):
        if board not in list(self.chats.keys()):
            self.chats[board] = archat.ARChat(board, len(self.chats), list(self.chats.keys()))

            for chat in self.chats.values():
                chat.addRoom(board)

    def switchTopic(self, forward = True):
        #TODO: fix
        keys = list(self.chats.keys())
        idx = keys.index(self.board)
        if forward:
            try:
                self.board = keys[idx+1]
            except IndexError:
                self.board = keys[0]
        else:
            try:
                self.board = keys[idx-1]
            except IndexError:
                self.board = keys[len(keys)-1]

        self.switch.emit(self.board)

    def stage(self, message : str):
        chat = self.chats[self.board]
        chat.stage(message)
        self.text = self.__parse__(message)
        self.emoji.emit(self.text[1])

    def send(self, blank=False):
        chat = self.chats[self.board]
        time = self.__time__()
        message, emojis = self.text
        datapacket = {
            "board"     :   self.board,
            "message_type" : "text",
            "sender" : self.user,
            "data" : message,
            "time" : time,
            "color": self.color, 
            "emoji": emojis
        }
        self.link.send(datapacket)
        chat.stage('')
        chat.post(self.user, message, self.color, time)
        print('sending: ' + message)

    def sendConstant(self):
        while True:
            t.sleep(1)
            link.send()
            

class BoardOverlay(QObject):
    board = pyqtSignal(np.ndarray)
    def __init__(self, topic='general', parent=None):
        super().__init__(parent)
        self.model = cv.imread(ROOT + 'model_qr.png')
        self.topic = topic
        self.path = ROOT + topic + '.jpg'

    # generates matches between two image descriptors
    # @param
    # des1: model image descriptors
    # des2: camera image descriptors
    def __match__(self, des1, des2):
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
    def __embed__(self, cameraimage, overlayimage, kp1, kp2, matches, augmentedimage, height, width):
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

    def changeTopic(self, topic):
        self.topic = topic
        self.path = ROOT + topic + '.jpg'

    def run(self, image):
        overlay = cv.imread(self.path)
        height, width, c = self.model.shape

        orb = cv.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(self.model, None) 

        overlay = cv.resize(overlay, (width, height))  # resize image to fit model image dimensions
        augmentedimage = image.copy()

        kp2, des2 = orb.detectAndCompute(image, None)
        matches = self.__match__(des1, des2)
        # print(len(matches))

        if len(matches) > 250:
            return self.__embed__(image, overlay, kp1, kp2, matches, augmentedimage, height, width)
        return image

    
