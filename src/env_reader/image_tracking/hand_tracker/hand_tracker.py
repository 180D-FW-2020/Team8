##
 #  File: hand_tracker.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 03 November 2020
 #  
 #  @brief 
 #

import cv2 as cv
import numpy as np
class hand_tracker:
    def __init__(self):
        self.camera = cv.VideoCapture(0)
        pass
    def __color_mask(self):
        pass
    def num_fingers(self):
        pass
    def hand_present(self):
        pass
    def location(self):
        pass

if __name__ == '__main__':
    print()
    #general testing for dev
    cap = cv.VideoCapture(0)

    # error opening
    if not (cap.isOpened()):
        print("Could not open video device")
    old_loc =(0,0)
    com = (0,0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # convert to hsv
        hsvim = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower = np.array([0,48,110],dtype="uint8")
        upper = np.array([20,255,255],dtype="uint8")
        skinRegionHSV = cv.inRange(hsvim, lower, upper)
        blurred = cv.blur(skinRegionHSV, (2,2)) #consider altering
        ret,thresh = cv.threshold(blurred,0,255,cv.THRESH_BINARY)

        # getting contours
        _, contours, _= cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours = max(contours, key=lambda x: cv.contourArea(x))
        #cv.drawContours(frame, [contours], -1, (255,255,0), 2)

        #get convex hull
        hull = cv.convexHull(contours, returnPoints=False)
        defects = cv.convexityDefects(contours, hull)
        points = []
        if defects is not None:
            cnt = 0
            for i in range(defects.shape[0]):  # calculate the angle
                s, e, f, d = defects[i][0]
                start = tuple(contours[s][0])
                end = tuple(contours[e][0])
                far = tuple(contours[f][0])
                a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  #      cosine theorem
                
                cv.line(frame,start,end,[0,255,0],2)
                cv.circle(frame,far,5,[0,0,255],-1)

                if angle <= 3*(np.pi) / 8:  # angle less than 90 degree, treat as fingers
                    cnt += 1
                    cv.circle(frame, far, 4, [255, 0 , 0], -1)
                    points.append( far)
            if cnt > 0:
                cnt = cnt+1

            old_loc = com
            if points:
                com = int(sum(i[0] for i in points)/len(points)), int(sum(i[1] for i in points)/len(points))
            else:
                com = (0,0)
            com_arr = np.asarray(com)
            old_loc_arr = np.asarray(old_loc)
            loc =  int(0.5*float(com_arr[0]) +0.5*float(old_loc_arr[0])), \
                   int(0.5*float(com_arr[1]) +0.5*float(old_loc_arr[1]))
            
            cv.circle(frame, loc, 4, [255, 255 , 0], -1)


            cv.putText(frame, str(cnt), (0, 50), cv.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0) , 2, cv.LINE_AA)
        hull = cv.convexHull(contours)
        #cv.drawContours(frame, [hull], -1, (0, 255, 255), 2)
        #cv.drawContours(frame, [contours], -1, (255, 0 , 255), 2)

        # Display the resulting frame
        cv.imshow('frame',frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()