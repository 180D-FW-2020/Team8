### A collection of methods for AR environment detection and interpretation ###
#
# part of the MEAT Project

import sys
import numpy as np
import cv2 as cv

## Global Vars ####################################################################################
isTesting = True
frameops = np.array(['']) # add strings to array to determine ops on frame

## Error Handlers #################################################################################
def displayError():
    print("ERR/DISPLAY: frame not read or read incorrectly.")


## Primary Methods ################################################################################
# create mask based on desired features
def drawMask():
    pass

# determine an amount of contours to return based on a given mask
def findContours():
    pass

# DESC: display handler, takes video input and draws scene based on desired specs
# PARAMS:
# isTesting: bool; if True, display output video feed
def drawScene(isTesting, frameops):
    cap = cv.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        if ret != True:
            displayError()

        # frame operations
        out = frame
        if frameops[0] == 'gray':
            out = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        elif frameops[0] == 'hsv':
            out = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        

        # display
        if isTesting:
            cv.imshow('frame', out)

        # press Q to quit the live video feed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
