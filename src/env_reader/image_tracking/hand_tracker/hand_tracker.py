##
 #  File: hand_tracker.py
 # 
 #  Author: Thomas Kost
 #  
 #  Date: 03 November 2020
 #  
 #  @brief track hands 
 #


import cv2 as cv
import numpy as np

class hand_tracker:

    def __init__(self, upper_HSV, lower_HSV, filter_coeff =[],debug=False):
        self.upper_HSV = upper_HSV
        self.lower_HSV = lower_HSV
        self.locations = []
        for i in range(len(filter_coeff)):
            self.locations.append((0,0))
        self.filter_coefficients = filter_coeff
        self.last_frame = []
        self.debugging = debug

    def __color_mask(self, frame):
        return cv.inRange(frame, self.lower_HSV, self.upper_HSV)

    def __blur(self, frame, blur_size = (2,2)):
        return cv.blur(frame, blur_size)

    def __bin_threshold(self, frame):
        _, thresh = cv.threshold(frame,0,255,cv.THRESH_BINARY)
        return thresh

    def num_fingers(self):
        return 0

    def open_hand_present(self):
        fingers = self.num_fingers()
        return (fingers <= 6) or (fingers >= 4)

    def __filter(self, values, filter_coeffs):
        acc0 = 0
        acc1 = 0
        for index, data_point in enumerate(values):
            acc0 += data_point[0]*filter_coeffs[index]
            acc1 += data_point[1]*filter_coeffs[index]
        return (int(acc0),int(acc1))

    def calibrate(self, upper_HSV, lower_HSV):
        self.upper_HSV = upper_HSV
        self.lower_HSV = lower_HSV
    
    def get_frame(self, frame):
        self.last_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        return

    def location(self):
        if self.last_frame.size == 0:
            print("Error: give hand tracker a frame! (get_frame)")
        # self.__get_frame()  ## now not needed
        masked = self.__color_mask(self.last_frame)
        blurred = self.__blur(masked)
        thresh = self.__bin_threshold(blurred)
        cv.imshow('frame',self.last_frame)
        cv.imshow('frame_2',masked)

        # getting contours
        contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if not contours:
           self.locations = np.roll(self.locations,1)
           self.locations[0] = self.locations[1]
           return (-1,-1)
        contours = max(contours, key=lambda x: cv.contourArea(x))
        #cv.drawContours(frame, [contours], -1, (255,255,0), 2)

        #get convex hull
        hull = cv.convexHull(contours, returnPoints=False)
        defects = cv.convexityDefects(contours, hull)
        points = []
        if defects is not None:
            cnt = 0
            for i in range(defects.shape[0]):  # calculate the angle
                s, e, f, _ = defects[i][0]
                start = tuple(contours[s][0])
                end = tuple(contours[e][0])
                far = tuple(contours[f][0])
                a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  #      cosine theorem
                
                if self.debugging:
                    cv.line(self.last_frame,start,end,[64,255,255],2)
                    cv.circle(self.last_frame,far,5,[0,255,255],-1)
    
                if angle <= 3*(np.pi) / 8:  # angle less than 90 degree, treat as fingers
                    cnt += 1
                    if self.debugging:
                        cv.circle(self.last_frame, far, 4, [120, 255 , 255], -1)
                    points.append( far)
            if cnt > 0:
                cnt = cnt+1
    
    
            if points:
                com = int(sum(i[0] for i in points)/len(points)), int(sum(i[1] for i in points)/len(points))
            else:
                com = self.locations[0] #assume no change

            self.locations = np.roll(self.locations, 1)
            self.locations[0] = com
    
            # filter
            loc = self.__filter(np.array(self.locations), self.filter_coefficients)

            
            if self.debugging:
                cv.circle(self.last_frame, loc, 4, [0, 0 , 255], -1)
                cv.putText(self.last_frame, str(cnt), (0, 50), cv.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0) , 2, cv.LINE_AA)

            cv.imshow('cur_frame', self.last_frame)
            return loc

if __name__ == '__main__':
    
    #general testing for dev
    lower = np.array([0,48,80],dtype="uint8")
    upper = np.array([20,255,255],dtype="uint8")
    filter_coeff = np.array([0.5,0.25, 0.25])
    ht = hand_tracker(upper, lower, filter_coeff, True)

    while(True):
        loc = ht.location()
       # Display the resulting frame
        cv.imshow('frame',cv.cvtColor(ht.last_frame,cv.COLOR_HSV2BGR))

        if cv.waitKey(1) & 0xFF == ord('q'):
             break

    cv.destroyAllWindows()