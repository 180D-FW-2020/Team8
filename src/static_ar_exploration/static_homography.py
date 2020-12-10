
# OpenCV homography functions
import cv2
import numpy as np

class ImageProcessor:

    def __init__(self, ipath, mpath):
        self.image = ipath
        self.model = mpath

    def findKeypoints(self):
        image = cv2.imread(self.image, 0)

        orb = cv2.ORB_create()                                              # make ORB detector
        keypoints = orb.detect(image, None)                                 # find keypoints
        keypoints, descriptors = orb.compute(image, keypoints)              # find descriptors
        keypointimg = cv2.drawKeypoints(image, keypoints, image)   # draw keypoints
        return keypointimg

    def getHomography(self, threshold):
        env = cv2.imread(self.image, 0)
        model = cv2.imread(self.model, 0)

        orb = cv2.ORB_create()
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)       # Hamming distance brute force

        kpframe, desframe = orb.detectAndCompute(env, None)
        kpmodel, desmodel = orb.detectAndCompute(model, None)

        matches = bf.match(desmodel, desframe)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) > threshold:
            matchimg = cv2.drawMatches(model, kpmodel, env, kpframe, matches[:threshold], 0, flags=2)
        else:
            print("not enough matches found")
            return

        sources = np.float32([kpmodel[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dests = np.float32([kpframe[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

        homography, msk = cv2.findHomography(sources, dests, cv2.RANSAC, 5.0)      # RANSAC for homography
        h, w = model.shape
        points = np.float32([[0,0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1,1,2)

        dest = cv2.perspectiveTransform(points, homography)
        env = cv2.polylines(env, [np.int32(dest)], True, 255, 3, cv2.LINE_AA)
        return (matchimg, env)
    
    def visualize(self, display):
        cv2.imshow('display', display)
        cv2.waitKey(10000)

    def cleanUp(self):
        cv2.destroyAllWindows()

if __name__ == '__main__':
    image = '/Users/michaelhuang/Desktop/Team8/src/static_ar_exploration/models_envs/env.png'      # change for your local path
    model = '/Users/michaelhuang/Desktop/Team8/src/static_ar_exploration/models_envs/model.png'    # change for your local path

    processor = ImageProcessor(image, model)
    keypointimg = processor.findKeypoints()
    matchimg, homographyimg = processor.getHomography(10)

    processor.visualize(homographyimg)
    processor.cleanUp()