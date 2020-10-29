
# OpenCV Keypoints
import cv2

class img_processor:

    def __init__(self, path):
        self.image_path = path

    def find_keypoints(self):
        image = cv2.imread(self.image_path)

        orb = cv2.ORB_create()                                              # make ORB detector
        keypoints = orb.detect(image, None)                                 # find keypoints
        keypoints, descriptors = orb.compute(image, keypoints)              # find descriptors
        image_with_keypoints = cv2.drawKeypoints(image, keypoints, image)   # draw keypoints
        return image_with_keypoints

    def visualize(self, image_with_keypoints):
        cv2.imshow('image_with_keypoints', image_with_keypoints)
        cv2.waitKey(10000)

    def clean_up(self):
        cv2.destroyAllWindows()

if __name__ == '__main__':
    image_path = '/Users/michaelhuang/Desktop/Team8/test.jpg'

    surface_detector = img_processor(image_path)
    img_w_kpts = surface_detector.find_keypoints()
    surface_detector.visualize(img_w_kpts)
    surface_detector.clean_up()


