import cv2 as cv
import json

class ARChat():
    def __init__(self):
        self.messages = []
        self.wordlimit = 46
    
    def queue(self, user, message, color, time, overflow=False):
        #timestamp = json.loads(time)
        if(len(user) + len(message) <= self.wordlimit):
            if(overflow == False):
                self.messages.insert(0, (user, message, color, "<" + time + ">"))
                #self.messages.insert(0, (user, message, color, "<" + timestamp["hour"] + ":" + timestamp["minute"] + ":" + timestamp["second"] + ">"))
            else:
                self.messages.insert(0, (" " * (len(user) + 12), message, color, ""))
        else:
            if(overflow == False):
                msg = self.processmsg(message)
                self.messages.insert(0, (user, msg[0], color, "<" + time + ">"))
                #self.messages.insert(0, (user, msg[0], color, "<" + timestamp["hour"] + ":" + timestamp["minute"] + ":" + timestamp["second"] + ">"))
                self.queue(user, msg[1], color, "", True)
            else:
                msg = self.processmsg(message)
                self.messages.insert(0, (" " * (len(user) + 12), msg[0], color, ""))
                self.queue(user, msg[1], color, "", True)
        print(self.messages)

    def processmsg(self, message):
        for i in range(self.wordlimit, 0, -1):
            if(message[i] == ' '):
                return (message[:i], message[i+1:])

    def write(self, im, out):
        index = 0
        for message in self.messages:
            if len(message[3]) != 0:
                cv.putText(im, message[3] + " " + message[0] + ": " + message[1], (20, im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            else:
                cv.putText(im, message[0] + message[1], (20, im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            index += 1
        cv.imwrite(out, im)


if __name__ == '__main__':
    chat = ARChat()
    #inputMsg = '{"message_type": "text", "sender": "John", "receiver": "Tyler", "data": "This is the message that will be displayed in AR chat", "time": {"hour": 1, "minute": 34, "second": 32}, "ID": 12345, "color": (255,0,0)}'
    inputMsg1 = '{"sender": "Nico", "data":"this is a test message", "time":"time"}'
    inputMsg2 = '{"sender": "Michael", "data":"this is another test message", "time":"time"}'
    inputMsg3 = '{"sender": "Nate", "data":"message", "time":"time"}'
    inputMsg4 = '{"sender": "Tommy", "data":"this is an overflowed message that has to be really long to show the overflow functionality built different", "time":"time"}'

    msg1 = json.loads(inputMsg1)
    msg2 = json.loads(inputMsg2)
    msg3 = json.loads(inputMsg3)
    msg4 = json.loads(inputMsg4)

    chat.queue(msg1["sender"], msg1["data"], (255,0,0), msg1["time"])
    chat.queue(msg2["sender"], msg2["data"], (255,255,0), msg2["time"])
    chat.queue(msg3["sender"], msg3["data"], (0,0,255), msg3["time"])
    chat.queue(msg4["sender"], msg4["data"], (0,255,0), msg4["time"])

    chat.write(cv.imread('img.jpg', 1), 'img_edited.jpg')
