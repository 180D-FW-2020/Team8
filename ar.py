
# OpenCV Keypoints
import cv2

image_path = '/Users/michaelhuang/Desktop/Team8/test.jpg'
image = cv2.imread(image_path)

orb = cv2.ORB_create()                                              # make ORB detector
keypoints = orb.detect(image, None)                                   # find keypoints
keypoints, descriptors = orb.compute(image, keypoints)              # find descriptors
image_with_keypoints = cv2.drawKeypoints(image, keypoints, image)   # draw keypoints

cv2.imshow('image w/keypoints', image_with_keypoints)

cv2.waitKey(10000)
cv2.destroyAllWindows()
