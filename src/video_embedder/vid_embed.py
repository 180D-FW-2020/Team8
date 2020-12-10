# vid_embed.py
# NAME: Michael Huang
# DESCRIPTION: video overlay on model surface in camera feed


import cv2
import numpy as np

# generates matches between two image descriptors
# @param
# des1: model image descriptors
# des2: camera image descriptors
def generateMatches(des1, des2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches

# does video embed in camera image
# @param
# model: model/reference image
# cameraimage: cap.read() camera image
# videoimage: video overlay read() image
# kp1: model keypoints
# kp2: camera image keypoints
# matches: BFMatcher between model and camera image descriptors
# augmentedimage: camera feed with video overlay
def embed(model, cameraimage, videoimage, kp1, kp2, matches, augmentedimage):
    srcpts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dstpts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    matrix, mask = cv2.findHomography(srcpts, dstpts, cv2.RANSAC, 5)

    points = np.float32([[0,0], [0,height], [width,height], [width,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(points, matrix)
    
    warpedimage = cv2.warpPerspective(videoimage, matrix, (cameraimage.shape[1], cameraimage.shape[0]))  # changes video frame shape into model surface

    newmask = np.zeros((cameraimage.shape[0], cameraimage.shape[1]), np.uint8)                        
    cv2.fillPoly(newmask, [np.int32(dst)], (255, 255, 255))
    invertedmask = cv2.bitwise_not(newmask)
    augmentedimage = cv2.bitwise_and(augmentedimage, augmentedimage, mask=invertedmask)                  
    augmentedimage = cv2.bitwise_or(warpedimage, augmentedimage)                                          
    return augmentedimage

# show image or video stream
# @param
# image: image/video to be displayed
# isVideo: bool determines if video or image
def showImage(image, isVideo = True):
    cv2.imshow('image', image)
    if isVideo:
        cv2.waitKey(1)
    else:
        cv2.waitKey(10000)



if __name__ == '__main__':
    cap = cv2.VideoCapture(0)                               # camera
    model = cv2.imread('model.png')                         # model image
    overlay = cv2.VideoCapture('video.mp4')                 # overlay video

    retval, videoimage = overlay.read()
    height, width, c = model.shape
    videoimage = cv2.resize(videoimage, (width, height))  # resize image to fit model image dimensions

    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(model, None)           

    targetDetected = False
    counter = 0

    while True:
        retval, cameraimage = cap.read()
        augmentedimage = cameraimage.copy()

        kp2, des2 = orb.detectAndCompute(cameraimage, None)

        if targetDetected == False:
            overlay.set(cv2.CAP_PROP_POS_FRAMES, 0)
            counter = 0
        else:
            if counter >= overlay.get(cv2.CAP_PROP_FRAME_COUNT):
                overlay.set(cv2.CAP_PROP_POS_FRAMES, 0)
                counter = 0
            retval, videoimage = overlay.read()
            videoimage = cv2.resize(videoimage, (width, height))           # resize video to fit model image dimensions

        matches = generateMatches(des1, des2)
        print(len(matches))

        if len(matches) > 230:
            targetDetected = True
            augmentedimage = embed(model, cameraimage, videoimage, kp1, kp2, matches, augmentedimage)                                                 
        
        showImage(augmentedimage)
        counter += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
