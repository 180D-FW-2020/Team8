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
        self.range_HSV = [10, 20, 20]
        self.locations = []
        for i in range(len(filter_coeff)):
            self.locations.append((0,0))
        self.filter_coefficients = filter_coeff
        self.debugging = debug

    def __color_mask(self, frame):
        return cv.inRange(frame, self.lower_HSV, self.upper_HSV)

    def __increment_HSV(self, pixel):
        last_HSV = (self.lower_HSV + self.upper_HSV)//2
        print(last_HSV)
        diff = np.subtract(last_HSV, pixel)
        print(diff)
        next_HSV = last_HSV - diff*0.1
        print(next_HSV)
        return np.array(next_HSV, dtype="int16")

    def __fix_mask(self, frame, loc):
        pixel = frame[loc]
        print(pixel)
        next_HSV = self.__increment_HSV(pixel)
        self.lower_HSV = np.array(np.maximum(next_HSV - self.range_HSV, [0, 0, 0]), dtype="int16")
        self.upper_HSV = np.array(np.minimum(next_HSV + self.range_HSV, [180, 200, 255]), dtype="int16")


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

    def __location(self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        masked = self.__color_mask(frame)
        blurred = self.__blur(masked)
        thresh = self.__bin_threshold(blurred)
        
        if self.debugging:
            cv.imshow('mask', masked)
        
        # getting contours
        _, contours, _= cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
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
                    cv.line(frame,start,end,[64,255,255],2)
                    cv.circle(frame,far,5,[0,255,255],-1)
    
                if angle <= 3*(np.pi) / 8:  # angle less than 90 degree, treat as fingers
                    cnt += 1
                    if self.debugging:
                        cv.circle(frame, far, 4, [120, 255 , 255], -1)
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
                cv.circle(frame, loc, 4, [0, 0 , 255], -1)
                cv.putText(frame, str(cnt), (0, 50), cv.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0) , 2, cv.LINE_AA)

            # self.__fix_mask(hsv, loc)

            return loc

    def resetMask(self, frame):
        pix_loc = frame.shape[0]//2, frame.shape[1]//2
        pixel = np.array(frame[pix_loc])

        self.lower_HSV = np.array(np.maximum(pixel - self.range_HSV, [0, 0, 0]), dtype="int16")
        self.upper_HSV = np.array(np.minimum(pixel + self.range_HSV, [180, 200, 255]), dtype="int16")


    def locAdder(self, frame):
        loc = self.__location(frame)
        return frame, loc

if __name__ == '__main__':
    
    cap = cv.VideoCapture(0)

    ret, frame = cap.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    pix_loc = frame.shape[0]//2, frame.shape[1]//2
    pixel = np.array(frame[pix_loc])
    # pixel = np.array([40, 100, 100])

    # hsvRange = np.array([10, 50, 50])
    # lower = np.array(np.maximum(pixel - hsvRange, [0, 0, 0]),dtype="int16")
    # upper = np.array(np.minimum(pixel + hsvRange, [180, 200, 255]), dtype="int16")

    lower = np.array([140, 48, 80], dtype="uint8")
    upper = np.array([180, 255, 255], dtype="uint8")

    #general testing for dev
    # filter_size = 5
    # filter_coeff = np.ones(filter_size, dtype="float32")/filter_size
    filter_coeff = [0.5, 0.25, 0.25]
    ht = hand_tracker(upper, lower, filter_coeff, True)

    while(True):
        ret, frame = cap.read()
        frame, _ = ht.locAdder(frame)

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        pix_loc = frame.shape[0]//2, frame.shape[1]//2

        # print(hsv[pix_loc])
        # Display the resulting frame
        cv.imshow('frame',frame)

        k = cv.waitKey(1)

        if k == ord('r'):
            ht.resetMask(frame)

        elif k == ord('q'):
             break

    cv.destroyAllWindows()