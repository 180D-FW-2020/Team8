import cv2
import numpy as np
from matplotlib import pyplot as plt

# read in image data through the on-board camera
cap = cv2.VideoCapture(0)
delta = 0
thrUp = 100
thrDn = 50

while(1):
    # take each frame
    ret, frame = cap.read()

    # convert to hsv
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dullKern = 1/9*np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dullGray = cv2.filter2D(gray, -1, dullKern)
    gauss = cv2.GaussianBlur(dullGray,(5,5),0)
    laplacian = cv2.Laplacian(gray, -1, delta = delta)

    #dull = cv2.filter2D(laplacian, -1, dullKern)
    #sharp = 2*laplacian - dull

    #ret,threshFrame = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    edgesX = cv2.Scharr(gauss,-1, 1, 0, delta=delta)
    edgesY = cv2.Scharr(gauss,-1, 0, 1, delta=delta)
    
    edgesMag = np.hypot(edgesX, edgesY)
    edgesMag = edgesMag/edgesMag.max()*255
    edgesMagImg = cv2.UMat(np.array(edgesMag, dtype=np.uint8))
    edgesAngle = np.array(np.arctan2(edgesY, edgesX)*180/np.pi, dtype = np.uint8)
    edgesCannyMag = cv2.Canny(cv2.UMat(np.array(edgesMag, dtype=np.uint8)), 100, 200)

    #edgesMagImg = cv2.UMat(edgesMag)
    #edgesMag = cv2.GaussianBlur(edgesMag,(5,5),0)
    #edgesAngleImg = cv2.UMat(edgesAngle)

    
    #kernel = np.array([[1, 0, -1], [0, 1, 0], [-1, 0, 1]])
    #kernel = np.array([[1, 4, 1], [0, 1, 0], [1, 4, 1]])
    #edgesFilter = cv2.filter2D(edgesAngle, -1, kernel)

    
    # code here from https://towardsdatascience.com/canny-edge-detection-step-by-step-in-python-computer-vision-b49c3a2d8123

    """
    edgesThin = edgesMag
    edgesCanny = edgesMag
    N = np.size(edgesMag[:,0])
    M = np.size(edgesMag[0,:])
    for i in range(N):
        for j in range(M):
            curMag = edgesMag[i,j]
            try:
                a = 255
                b = 255 
                
                curAngle = edgesMag[i,j]
                if(0 <= curAngle < 22.5 and 157.5 <= curAngle <= 180):
                    a = edgesMag[i, j-1]
                    b = edgesMag[i,j+1]
                elif(22.5 <= curAngle < 67.5):
                    a = edgesMag[i-1, j+1]
                    b = edgesMag[i+1,j-1]
                elif(67.5 <= curAngle < 112.5):
                    a = edgesMag[i-1 , j]
                    b = edgesMag[i + 1,j]
                elif(112.5 <= curAngle < 157.5):
                    a = edgesMag[i-1, j-1]
                    b = edgesMag[i+1,j+1]

                if(curMag > a and curMag > b):
                    pass
                else:
                    edgesThin[i,j] = 0

            except IndexError as err:
                pass

        #end code from source
    
    for i in range(N):
        for j in range(M):
            curMag = edgesThin[i,j]
            if(curMag < thrDn):
                edgesThin[i,j] = 0
            elif(thrDn <= curMag < thrUp):
                edgesThin[i, j] = 127
            elif(curMag >= thrUp):
                edgesThin[i,j] = 255
    """
    """
    for i in range(N):
        for j in range(M):
            try:
                if(edgesThin[i,j-1] == 255 or edgesThin[i,j+1] == 255 or edgesThin[i-1,j-1] == 255 or edgesThin[i+1,j-1] == 255 or 
                    edgesThin[i-1,j+1] == 255 or edgesThin[i+1,j+1] == 255 or edgesThin[i-1,j] == 255 or edgesThin[i+1,j] == 255):
                    edgesCanny[i,j] = 255
                else:
                    edgesCanny[i,j] = 0
            except IndexError as err:
                pass
    """
                
    # throw through canny filter
    canny = cv2.Canny(gray, 100, 200)
    #edgesAngleImg = edgesAngle*255/180
    #edgesCannyImg = cv2.UMat(np.array(edgesCanny, np.uint8))
    #edgesThinImg = cv2.UMat(np.array(edgesThin, np.uint8))

    # shows
    #cv2.imshow('sharp', sharp)
    cv2.imshow('X', edgesX)
    cv2.imshow('Y', edgesY)
    cv2.imshow('Mag', edgesMagImg)
    cv2.imshow('frame',frame)
    cv2.imshow('phase', edgesAngle)
    cv2.imshow('laplacian', laplacian)
    #cv2.imshow('filter',edgesFilter)
    #cv2.imshow('thin', edgesThinImg)
    #cv2.imshow('myCanny', edgesCannyMag)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()