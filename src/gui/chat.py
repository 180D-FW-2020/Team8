import sys

PATH = [
    "src/gui",
    "test"
]

for lib in PATH:
    sys.path.append(lib)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import cv2 as cv

import mqtt
import chat_image
import numpy as np
from datetime import time
import stringparser

## Globals #######################################################################################################
## a list of globals used in this file

DELIM = "slash"
TOPICPREF = "ece180d/MEAT/"
ROOT = "./data/gui/"
EMOTEIDS = {
    ":/emotes/angry"        : 1 ,
    ":/emotes/cringe"       : 2 ,
    ":/emotes/cry"          : 3 ,
    ":/emotes/doubt"        : 4 ,
    ":/emotes/LOL"          : 5 ,
    ":/emotes/welp"         : 6 ,
    ":/emotes/frown"        : 7 ,
    ":/emotes/grin"         : 8 ,
    ":/emotes/love"         : 9 ,
    ":/emotes/ofcourse"     : 10,           
    ":/emotes/shock"        : 11,
    ":/emotes/simp"         : 12,
    ":/emotes/smile"        : 13,
    ":/emotes/hmmm"         : 14,
    ":/emotes/tongue"       : 15,
    ":/emotes/wink"         : 16        
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
    "chat"      :   chat_image.ARChat}
            }

class BoardManager(QObject):
    update = pyqtSignal(str)
    def __init__(self, user, color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)), parent=None):
        super().__init__(parent)
 
        self.user = user
        self.color = color
        self.topic = "general"
        self.boards = {}

        self.createBoard(self.topic)

    def __time__(self):
        now = time.now()
        return { "hour": now.hour, "minute": now.minute, "second": now.second }

    def __receive__(self, topic, message):
        print("entered receive")
        try:
            board = self.boards[topic]
        except KeyError:
            print("Whoa! Looks like there isn't a board with that topic.")
        
        user = message['sender']
        color = message['color']
        time = message['time']
        text = message['data']
        emojis = message['emoji']

        board["chat"].queue(user, text, color, time)
        if self.topic is topic:
            board["chat"].write()

    def __parse__(self, message):
        out = stringparser.parse_string(message, DELIM, EMOTEID)
        text = out[0]
        emojis = out[1]
        return text, emojis

    def createBoard(self, topic:str):
        self.boards[topic] = {
            "link"       :   mqtt.MQTTLink(TOPICPREF + topic),
            "chat"      :   chat_image.ARChat(ROOT + topic)
            }
        self.boards[topic]["link"].message.connect(lambda x: self.__receive__(topic, x))

    def switchTopic(self, forward = True):
        #TODO: fix
        keys = self.boards.keys()
        idx = keys.index(self.topic)
        if forward:
            try:
                self.topic = keys[idx+1]
            except IndexError:
                self.topic = keys[0]
        else:
            try:
                self.topic = keys[idx-1]
            except IndexError:
                self.topic = keys[len(keys)-1]

        boards[self.topic]["chat"].write()
        self.update.emit(self.topic)

    def send(self, message : str):
        board = self.boards[self.topic]
        time = self.__time__()
        message, emojis = self.__parse__(message)
        msg = {
            "message_type" : "text",
            "sender" : self.user,
            "data" : message,
            "time" : time,
            "color": self.color, 
            "emoji": emojis
        }
        
    #TODO: figure out sending/confirm sending

    

class BoardOverlay(QObject):
    board = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = cv.imread('data/gui/model_qr.png')
        overlay = cv.imread('data/gui/general.jpg')
        if overlay.any() == None:
            cv.imwrite('data/gui/general.jpg', self.model)
            self.overlay = self.model
        else:
            self.overlay = overlay
        self.topic = "general"
        self.board_root = "data/gui/"

    def changeTopic(self, topic):
        self.topic = topic
        self.overlay = cv.imread(os.path.join(self.board_root, self.topic))

    def run(self, image):
        overlay = cv.imread(self.board_root + self.topic + '.jpg')
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

    
