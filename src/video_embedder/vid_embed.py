import cv2
import numpy as np

# @param
# des1: model image descriptors
# des2: camera image descriptors
def generateMatches(des1, des2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches

# @param
# model: model/reference image
# camera_image: cap.read() camera image
# video_image: video overlay read() image
# kp1: model keypoints
# kp2: camera image keypoints
# matches: BFMatcher between model and camera image descriptors
# augmented_image: camera feed with video overlay
def embed(model, camera_image, video_image, kp1, kp2, matches, augmented_image):
    srcpts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dstpts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    matrix, mask = cv2.findHomography(srcpts, dstpts, cv2.RANSAC, 5)

    points = np.float32([[0,0], [0,height], [width,height], [width,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(points, matrix)
    
    warped_image = cv2.warpPerspective(video_image, matrix, (camera_image.shape[1], camera_image.shape[0]))  # changes video frame shape into model surface

    new_mask = np.zeros((camera_image.shape[0], camera_image.shape[1]), np.uint8)                        # mask of video projection space
    cv2.fillPoly(new_mask, [np.int32(dst)], (255, 255, 255))
    inverted_mask = cv2.bitwise_not(new_mask)
    augmented_image = cv2.bitwise_and(augmented_image, augmented_image, mask=inverted_mask)                   # black out projection space
    augmented_image = cv2.bitwise_or(warped_image, augmented_image)                                          # overlay image over webcam
    return augmented_image

# @param
# image: image/video to be displayed
# is_video: bool determines if video or image
def show(image, is_video = True):
    cv2.imshow('image', image)
    if is_video:
        cv2.waitKey(1)
    else:
        cv2.waitKey(10000)



if __name__ == '__main__':
    cap = cv2.VideoCapture(0)                               # camera
    model = cv2.imread('model.png')                         # model image
    overlay_video = cv2.VideoCapture('video.mp4')           # overlay video

    retval, video_image = overlay_video.read()
    height, width, c = model.shape
    video_image = cv2.resize(video_image, (width, height))  # resize image to fit model image dimensions

    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(model, None)           # keypoints and descriptors

    target_detected = False
    frame_counter = 0

    while True:
        retval, camera_image = cap.read()
        augmented_image = camera_image.copy()

        kp2, des2 = orb.detectAndCompute(camera_image, None)

        if target_detected == False:
            overlay_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_counter = 0
        else:
            if frame_counter >= overlay_video.get(cv2.CAP_PROP_FRAME_COUNT):
                overlay_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_counter = 0
            retval, video_image = overlay_video.read()
            video_image = cv2.resize(video_image, (width, height))           # resize video to fit model image dimensions

        matches = generateMatches(des1, des2)
        print(len(matches))

        if len(matches) > 230:
            target_detected = True
            augmented_image = embed(model, camera_image, video_image, kp1, kp2, matches, augmented_image)                                                 
        
        show(augmented_image)
        frame_counter += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
