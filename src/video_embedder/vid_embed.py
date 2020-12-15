# vid_embed.py
# NAME: Michael Huang
# DESCRIPTION: video overlay on model surface in camera feed


import cv2
import numpy as np

class VideoEmbedder:

    # @param
    # cap: camera stream capture
    # model: reference image to be projected upon
    # overlay: video(s) to be overlayed
    def __init__(self, cap, model, overlay):
        self.cap = cap
        self.model = model
        self.overlay = overlay

    # run video embedder
    def run(self):
        i = 0                                               # index for vid carousel
        height, width, c = self.model.shape
        #videoimage = cv2.resize(videoimage, (width, height))  # resize image to fit model image dimensions

        orb = cv2.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(self.model, None)           

        targetDetected = False
        counter = 0

        while True:
            retval, videoimage = self.overlay[i].read()
            retval, cameraimage = self.cap.read()
            augmentedimage = cameraimage.copy()

            kp2, des2 = orb.detectAndCompute(cameraimage, None)

            if targetDetected == False:
                self.overlay[i].set(cv2.CAP_PROP_POS_FRAMES, 0)
                counter = 0
            else:
                if counter >= self.overlay[i].get(cv2.CAP_PROP_FRAME_COUNT):
                    self.overlay[i].set(cv2.CAP_PROP_POS_FRAMES, 0)
                    counter = 0
                retval, videoimage = self.overlay[i].read()
                videoimage = cv2.resize(videoimage, (width, height))           # resize video to fit model image dimensions

            matches = self.generateMatches(des1, des2)
            #print(len(matches))

            if len(matches) > 230:
                targetDetected = True
                augmentedimage = self.embed(cameraimage, videoimage, kp1, kp2, matches, augmentedimage, height, width)                                                 
            
            self.showImage(augmentedimage)
            counter += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # makeshift carousel transition - replace with signal
            if cv2.waitKey(1) & 0xFF == ord('a'):
                i = 1
            if cv2.waitKey(1) & 0xFF == ord('b'):
                i = 0

    # generates matches between two image descriptors
    # @param
    # des1: model image descriptors
    # des2: camera image descriptors
    def generateMatches(self, des1, des2):
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
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
        matrix, mask = cv2.findHomography(srcpts, dstpts, cv2.RANSAC, 5)

        points = np.float32([[0,0], [0,height], [width,height], [width,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(points, matrix)
        
        warpedimage = cv2.warpPerspective(videoimage, matrix, (cameraimage.shape[1], cameraimage.shape[0]))  # changes video frame shape into model surface

        newmask = np.zeros((cameraimage.shape[0], cameraimage.shape[1]), np.uint8)                        
        cv2.fillPoly(newmask, [np.int32(dst)], (255, 255, 255))
        invertedmask = cv2.bitwise_not(newmask)
        cv2.imshow('mask', invertedmask)
        augmentedimage = cv2.bitwise_and(augmentedimage, augmentedimage, mask=invertedmask)
        augmentedimage = cv2.bitwise_or(warpedimage, augmentedimage)  
        return augmentedimage

    # show image or video stream
    # @param
    # image: image/video to be displayed
    # isVideo: bool determines if video or image
    def showImage(self, image, isVideo = True):
        cv2.imshow('image', image)
        if isVideo:
            cv2.waitKey(1)
        else:
            cv2.waitKey(10000)