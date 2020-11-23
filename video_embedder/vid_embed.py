import cv2
import numpy as np

cap = cv2.VideoCapture(0)                   # camera
imgTarget = cv2.imread('model.png')         # model image
myVid = cv2.VideoCapture('video.mp4')       # overlay video

detection = False                           # is target in webcam image
frameCounter = 0

success, imgVideo = myVid.read()
hT, wT, cT = imgTarget.shape
imgVideo = cv2.resize(imgVideo, (wT, hT))   # resize image to fit model image dimensions

orb = cv2.ORB_create(nfeatures=1000)
kp1, des1 = orb.detectAndCompute(imgTarget, None)       # keypoints and descriptors
imgTarget = cv2.drawKeypoints(imgTarget, kp1, None)     # test keypoints

while True:
    success, imgWebcam = cap.read()
    imgAug = imgWebcam.copy()
    kp2, des2 = orb.detectAndCompute(imgWebcam, None)
    imgWebcam = cv2.drawKeypoints(imgWebcam, kp2, None)     # test keypoints

    if detection == False:
        myVid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frameCounter = 0
    else:
        if frameCounter == myVid.get(cv2.CAP_PROP_FRAME_COUNT):
            myVid.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frameCounter = 0
        success, imgVideo = myVid.read()
        imgVideo = cv2.resize(imgVideo, (wT, hT))           # resize video to fit model image dimensions


    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    print(len(matches))

    if len(matches) > 220:
        detection = True
        imgFeatures = cv2.drawMatches(imgTarget, kp1, imgWebcam, kp2, matches[:15], None, flags=2)

        srcpts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dstpts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        matrix, mask = cv2.findHomography(srcpts, dstpts, cv2.RANSAC, 5)
        # print(matrix)

        pts = np.float32([[0,0], [0,hT], [wT,hT], [wT,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, matrix)
        img2 = cv2.polylines(imgWebcam, [np.int32(dst)], True, (255,0,255), 3)

        imgWarp = cv2.warpPerspective(imgVideo, matrix, (imgWebcam.shape[1], imgWebcam.shape[0]))   # changes video frame shape into model surface

        maskNew = np.zeros((imgWebcam.shape[0], imgWebcam.shape[1]), np.uint8)                      # mask of video projection space
        cv2.fillPoly(maskNew, [np.int32(dst)], (255, 255, 255))
        maskInv = cv2.bitwise_not(maskNew)
        imgAug = cv2.bitwise_and(imgAug, imgAug, mask=maskInv)                                      # black out projection space
        imgAug = cv2.bitwise_or(imgWarp, imgAug)                                                    # overlay image over webcam

    # cv2.imshow('maskNew', maskNew)
    # cv2.imshow('imgWarp', imgWarp)
    # cv2.imshow('img2', img2)
    # cv2.imshow('imgFeatures', imgFeatures)
    # cv2.imshow('imgTarget', imgTarget)
    # cv2.imshow('imgVideo', imgVideo)
    # cv2.imshow('imgWebcam', imgWebcam)
    cv2.imshow('imgAug', imgAug)
    cv2.waitKey(1)
    frameCounter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
