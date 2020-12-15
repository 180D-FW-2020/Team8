# MOVE INTO src/video_embedder DIR TO TEST

from vid_embed import VideoEmbedder
import cv2
import numpy as np

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)                               # camera
    model = cv2.imread('model.png')                         # model image
    carousel = [cv2.VideoCapture('video.mp4'), cv2.VideoCapture('video2.mp4')]                # overlay video(s)

    vidEmbedder = VideoEmbedder(cap, model, carousel)
    vidEmbedder.run()

    cap.release()
    cv2.destroyAllWindows()
