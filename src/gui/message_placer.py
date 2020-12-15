import cv2 as cv
import numpy as np

# an extention of mqtt_link.py, meant to place such an outputted message on an image

class MessagePlacer:
    def __get_window_loc(self, frame_shape):
        if "l" in self.window_loc:
            x = 0
        elif "r" in self.window_loc:
            x = frame_shape[1] - self.window_shape[0]
        else:
            print("Error: Must have r or l")
        
        if "t" in self.window_loc:
            y = 0
        elif "b" in self.window_loc:
            y = frame_shape[0] - self.window_shape[1]
        else:
            print("Error: Must have t or b")

        return y, x


    def __init__(self, window_loc = "tl", max_messages = 5):
        self.max_messages = max_messages
        self.font = cv.FONT_HERSHEY_SIMPLEX
        self.font_size = 0.5
        self.font_thick = 1
        self.line_type = cv.LINE_AA
        self.color = (255, 255, 255)
        self.ws = 2                                 # number of text lines between user input and output

        self.text_buffer = self.font_size*40
        self.window_shape = (int((self.max_messages + self.ws + 2)*self.text_buffer), 200)
        self.window_loc = window_loc


    def __make_mask(self, frame_shape, window_start):
        mask = np.ones(frame_shape, np.uint8)
        mask[window_start[0] : (window_start[0] + self.window_shape[0]), window_start[1] : (window_start[1] + self.window_shape[1])] = 0
        return mask

    def __place_mask(self, frame, mask):
        return cv.bitwise_and(frame,frame, mask=mask)

    def __find_origin(self, window_start, num):
        # this works and I don't know why - sorry u debugging losers
        x = int( window_start[0] + (num + 1 ) * self.text_buffer )
        y = int( window_start[1] + self.text_buffer )
        return (y, x)

    def __place_text(self, message, frame, window_start, num):
        text_origin = self.__find_origin(window_start, num)
        cv.putText(frame,message,text_origin, self.font, self.font_size, self.color, self.font_thick, self.line_type) 
        return frame 

    def placeUserMessage(self, message, frame):
        window_start = self.__get_window_loc(frame.shape[:2])
        return self.__place_text(message, frame, window_start, self.max_messages + self.ws)

    def placeMessages(self, message_list, frame):
        frame_shape = frame.shape[:2]

        # find the location where the rectangle should go
        window_start = self.__get_window_loc(frame_shape)

        # get mask and place the mask in the frame
        mask = self.__make_mask(frame_shape, window_start)
        mask_im = self.__place_mask(frame, mask)

        for index, message in enumerate(message_list):
            text_frame = self.__place_text(message, mask_im, window_start, index)
        
        return mask_im

if __name__ == "__main__":
    message_list = ["let them eat cake", "let them eat cake 2","let them eat cake 3","let them eat cake 4","let them eat cake 5"]
    cap = cv.VideoCapture(0)

    ret, frame = cap.read()

    placer = MessagePlacer(frame.shape[:2], "br")
        
    message_frame = placer.placeMessages(message_list, frame)
    user_frame = placer.placeUserMessage("i eat poop", message_frame)
    
    while(1):
        cv.imshow("message frame", message_frame)
        cv.imshow("user frame", user_frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()
