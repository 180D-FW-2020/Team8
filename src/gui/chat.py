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
import datetime


EMPTYBOARD = {  
    "topic"     :
    {"net"      :   mqtt.MQTTNetObject, 
    "chat"      :   chat_image.ARChat}
            }

class BoardManager(QObject):
    topic = pyqtSignal(str)
    def __init__(self, user, parent=None):
        super().__init__(parent)

        self.root = "./data/gui/chat.jpg"
        self.topic_prefix = "ece180d/MEAT/"
        self.user = user
        self.topic = "general"
        self.boards = {"general": 
            {
            "net"       :   mqtt.MQTTNetObject(board = self.topic_prefix + "general", user=user, 
                                color = (np.random.rand(), np.random.rand(), np.random.rand())),
            "chat"      :   chat_image.ARChat(self.root)
            }
        }

        self.gesturer = mqtt.MQTTIMUObject(board = self.topic_prefix + "general/gesture", user = user)
        self.gesturer.gestup.connect(lambda x: self.switchTopic(x))

    def createBoard(self, topic:str):
        self.boards[topic] = {
            "net"       :   mqtt.MQTTNetObject(self.topic_prefix + topic, self.user, 
                                color = (np.random.rand(), np.random.rand(), np.random.rand())),
            "chat"      :   chat_image.ARChat(self.root)
            }
        self.boards[topic]["net"].receive.connect(lambda x: self.receivePost(topic, x))


    def switchTopic(self, forward):
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
        self.topic.emit(self.topic)

    def userPost(self, message):
        board = self.boards[self.topic]
        board["net"].sendMessage(message)

        user = board["net"].messages["senderID"]
        color = board["net"].getColor()
        now = datetime.datetime.now()
        time = {
                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            }

        board["chat"].queue(user, message, color, time)
        board["chat"].write()

    def receivePost(self, topic, message):
        board = self.boards[topic]
        user = message['sender']
        color = message['color']
        time = message['time']
        board["chat"].queue(user, message, color, time)

        if self.topic is topic:
            board["chat"].write()

class BoardOverlay(QObject):
    board = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = cv.imread('../../data/gui/model_qr.png')
        self.overlay = cv.imread('path/to/original/overlay')
        self.topic = "general"
        self.board_root = "path"

    def changeTopic(self, topic):
        self.topic = topic
        self.overlay = cv.imread(os.path.join(self.board_root, self.topic))

    def run(self, image):
        overlay = cv.imread(self.board_root + self.topic)
        height, width, c = self.model.shape

        orb = cv.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(self.model, None) 

        overlay = cv.resize(overlay, (width, height))  # resize image to fit model image dimensions
        augmentedimage = cameraimage.copy()

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

    
