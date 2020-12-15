import cv2 as cv
import numpy as np

# an extention of mqtt_link.py, meant to place such an outputted message on an image
# frame implied to be a frame from opencv 
# only money works on gypsies

class BoxPlacer:
    def __init__(self, box_shape, box_loc="tl"):
        self.box_shape = box_shape
        self.box_loc = box_loc

    def __get_box_loc(self, frame_shape):
        if "l" in self.box_loc:
            x = 0
        elif "r" in self.box_loc:
            x = frame_shape[1] - self.box_shape[0]
        else:
            print("Error: Must have r or l")
        
        if "t" in self.box_loc:
            y = 0
        elif "b" in self.box_loc:
            y = frame_shape[0] - self.box_shape[1]
        else:
            print("Error: Must have t or b")

        return y, x

    def __make_mask(self, frame_shape, box_loc):
        mask = np.ones(frame_shape, np.uint8)
        mask[box_loc[0] : (box_loc[0] + self.box_shape[0]), box_loc[1] : (box_loc[1] + self.box_shape[1])] = 0
        return mask

    def placeBox(self, frame):
        frame_shape = frame.shape[:2]
        box_loc = self.__get_box_loc(frame_shape)
        mask = self.__make_mask(frame_shape, box_loc)
        return cv.bitwise_and(frame,frame, mask=mask), box_loc

class TextPlacer:
    def __init__(self, line_length, max_lines): # window coord is in row#, col#
        self.line_length = line_length
        self.max_lines = max_lines
        self.font = cv.FONT_HERSHEY_SIMPLEX
        self.font_size = 0.25                     
        self.font_thick = 1
        self.line_type = cv.LINE_AA
        self.color = (255, 255, 255)
        self.ws = 2                                 # number of text lines between user input and output

        self.text_buffer = self.font_size*40
        self.cpl = int((10//self.font_size) * (self.line_length//200))       # characters per line (cpl) conversion: 10 characters at size 1 font per line with line length == 200

    def __find_origin(self, text_loc, num):
        # this works and I don't know why - sorry u debugging losers
        x = int( text_loc[0] + (num + 1 ) * self.text_buffer )
        y = int( text_loc[1] + self.text_buffer )
        return (y, x)

    def __split_message(self, message, lines_list):
        if len(message) > self.cpl:
            lines_list.append(message[:self.cpl])
            next_message = "    " + message[self.cpl:]
            lines_list = self.__split_message(next_message, lines_list)
        else:
            lines_list.append(message)
        return lines_list

    def __get_message_lines(self, message_list):
        lines_list = []
        for message in message_list:
            lines_list = self.__split_message(message, lines_list)
        return lines_list

    def __place_text(self, frame, message, text_loc, num):
        text_origin = self.__find_origin(text_loc, num)
        cv.putText(frame, message, text_origin, self.font, self.font_size, self.color, self.font_thick, self.line_type) 
        return frame 

    # def placeUserMessage(self, message, frame):
    #     return self.__place_text(message, frame, text_loc, self.max_messages + self.ws)

    def placeMessages(self, frame, message_list, text_loc):
        new_list = self.__get_message_lines(message_list)
        new_list = new_list[:self.max_lines]

        for index, message in enumerate(new_list):
            frame = self.__place_text(frame, message, text_loc, index)
        
        return frame

class BoardPlacer:
    def __init__(self, box_shape, box_loc="br", max_lines=5):
        self.box_placer = BoxPlacer(box_shape, box_loc)
        self.text_placer = TextPlacer(box_shape[1], max_lines)
        self.max_lines = max_lines
        self.box_shape = box_shape
        self.board = {"user":[], "chat":[]}
    
    def __get_user_loc(self, box_loc):
        x = box_loc[0] + int(3*self.box_shape[0]/4)
        y = box_loc[1]
        return x, y

    def updateChatBoard(self, message):
        self.board["chat"].append(message)
        if len(self.board["chat"]) > self.max_lines:
            del self.board["chat"][0]

    def updateUserBoard(self, message_list):
        self.board["user"] = message_list

    def placeBoard(self, frame):
        # first, place box on frame
        masked_frame, box_loc = self.box_placer.placeBox(frame)

        user_loc = self.__get_user_loc(box_loc)

        # then, get text 
        text_frame = self.text_placer.placeMessages(masked_frame, self.board["chat"], box_loc)
        utext_frame = self.text_placer.placeMessages(text_frame, self.board["user"], user_loc)

        return utext_frame


if __name__ == "__main__":
    message_list = ["let them eat cake", "let them eat cake 2","let them eat cake 3","let them eat cake 4","let them eat cake 5"]
    message_list_2 = ["I ate a pear today, it was delicious. I hope one day you can eat pears too! This is to continue the message size and see what happens", "Do not forget about the oven"]
    cap = cv.VideoCapture(0)

    ret, frame = cap.read()

    box_size = (200, 200)
    placer = BoardPlacer(box_size)

    for message in message_list_2:
        placer.updateChatBoard(message)

    placer.updateUserBoard(["holy shit if this works"])

    text_frame = placer.placeBoard(frame)
    
    while(1):
        # cv.imshow("message frame", message_frame)
        cv.imshow("texted frame", text_frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()
