
# OpenCV homography functions
import cv2
import numpy as np

class img_processor:

    def __init__(self, i_path, m_path):
        self.image_path = i_path
        self.model_path = m_path

    def find_keypoints(self):
        image = cv2.imread(self.image_path, 0)

        orb = cv2.ORB_create()                                              # make ORB detector
        keypoints = orb.detect(image, None)                                 # find keypoints
        keypoints, descriptors = orb.compute(image, keypoints)              # find descriptors
        image_with_keypoints = cv2.drawKeypoints(image, keypoints, image)   # draw keypoints
        return image_with_keypoints

    def get_homography(self, threshold):
        env = cv2.imread(self.image_path, 0)
        model = cv2.imread(self.model_path, 0)

        orb = cv2.ORB_create()
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)       # Hamming distance brute force

        kp_frame, des_frame = orb.detectAndCompute(env, None)
        kp_model, des_model = orb.detectAndCompute(model, None)

        matches = bf.match(des_model, des_frame)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) > threshold:
            match_image = cv2.drawMatches(model, kp_model, env, kp_frame, matches[:threshold], 0, flags=2)
        else:
            print("not enough matches found")
            return

        sources = np.float32([kp_model[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dests = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

        homography, msk = cv2.findHomography(sources, dests, cv2.RANSAC, 5.0)      # RANSAC for homography
        h, w = model.shape
        points = np.float32([[0,0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1,1,2)

        dest = cv2.perspectiveTransform(points, homography)
        env = cv2.polylines(env, [np.int32(dest)], True, 255, 3, cv2.LINE_AA)
        return (match_image, env)
    
    def visualize(self, display_img):
        cv2.imshow('display_img', display_img)
        cv2.waitKey(10000)

    def clean_up(self):
        cv2.destroyAllWindows()

if __name__ == '__main__':
    image_path = '/Users/michaelhuang/Desktop/Team8/static_exploration/models_envs/env.png'
    model_path = '/Users/michaelhuang/Desktop/Team8/static_exploration/models_envs/model.png'

    surface_detector = img_processor(image_path, model_path)
    img_w_kpts = surface_detector.find_keypoints()
    match_img, homo_img = surface_detector.get_homography(10)

    surface_detector.visualize(homo_img)
    surface_detector.clean_up()