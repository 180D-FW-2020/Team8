import sys
import time
from os import path
import cv2 as cv
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading

# @desc
# test class for opencv video feed with ar video overlay
# todo: video lag, overlay video not playing
class VideoOverlayCarousel(QObject):
    image_data = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv.VideoCapture(0)
        self.model = cv.imread('model.png')
        self.overlay = [cv.VideoCapture('video.mp4'), cv.VideoCapture('video2.mp4')]
        self.counter = 0
        self.trigger = QBasicTimer()

    # @desc
    # event trigger for an instantaneous event; use when an event overload is not desired
    # or when an event trigger must cause a custom signal to emit
    def start(self):
        self.trigger.start(0, self)

    # run video embedder
    def run(self, videoimage, cameraimage):
        i = 1                                               # index for vid carousel
        height, width, c = self.model.shape

        orb = cv.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(self.model, None)           

        targetDetected = False
        videoimage = cv.resize(videoimage, (width, height))  # resize image to fit model image dimensions
        augmentedimage = cameraimage.copy()

        kp2, des2 = orb.detectAndCompute(cameraimage, None)

        if targetDetected == False:
            self.overlay[i].set(cv.CAP_PROP_POS_FRAMES, 0)
            self.counter = 0
        else:
            if self.counter >= self.overlay[i].get(cv.CAP_PROP_FRAME_COUNT):
                self.overlay[i].set(cv.CAP_PROP_POS_FRAMES, 0)
                self.counter = 0
            self.overlay[i].set(cv.CAP_PROP_POS_FRAMES, self.counter)
            retval, videoimage = self.overlay[i].read()
            videoimage = cv.resize(videoimage, (width, height))           # resize video to fit model image dimensions

        matches = self.generateMatches(des1, des2)
        #print(len(matches))

        if len(matches) > 230:
            targetDetected = True
            augmentedimage = self.embed(cameraimage, videoimage, kp1, kp2, matches, augmentedimage, height, width)                                                 
        
        self.counter += 1
        return augmentedimage

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
    # videoimage: video overlay read() image
    # kp1: model keypoints
    # kp2: camera image keypoints
    # matches: BFMatcher between model and camera image descriptors
    # augmentedimage: camera feed with video overlay
    # height: height of mask
    # width: width of mask
    def embed(self, cameraimage, videoimage, kp1, kp2, matches, augmentedimage, height, width):
        srcpts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dstpts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        matrix, mask = cv.findHomography(srcpts, dstpts, cv.RANSAC, 5)

        points = np.float32([[0,0], [0,height], [width,height], [width,0]]).reshape(-1,1,2)
        dst = cv.perspectiveTransform(points, matrix)
        
        warpedimage = cv.warpPerspective(videoimage, matrix, (cameraimage.shape[1], cameraimage.shape[0]))  # changes video frame shape into model surface

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

        retval, videoimage = self.overlay[1].read()
        retval, cameraimage = self.cap.read()
        augmentedimage = self.run(videoimage, cameraimage)
        self.image_data.emit(augmentedimage)