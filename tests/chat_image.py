import cv2 as cv
import json

class ARChat():
    def __init__(self, path):
        self.messages = []
        self.rooms = []
        self.wordlimit = 64
        self.boardpath = path

    def getPath(self):
        return self.boardpath
    
    # queue mqtt message for chatboard placement
    def queue(self, user, message, color, timestamp, overflow=False):
        h = ""
        m = ""
        s = ""
        if(len(user) + len(message) <= self.wordlimit):
            if(overflow == False):
                h = str(timestamp["hour"])
                m = str(timestamp["minute"])
                s = str(timestamp["second"])
                if(len(str(timestamp["hour"])) == 1):
                    h = '0' + str(timestamp["hour"])
                if(len(str(timestamp["minute"])) == 1):
                    m = '0' + str(timestamp["minute"])
                if(len(str(timestamp["second"])) == 1):
                    s = '0' + str(timestamp["second"])
                self.messages.insert(0, (user, message, color, "<" + h + ":" + m + ":" + s + ">"))
            else:
                self.messages.insert(0, ("", message, color, ""))
        else:
            if(overflow == False):
                h = str(timestamp["hour"])
                m = str(timestamp["minute"])
                s = str(timestamp["second"])
                if(len(str(timestamp["hour"])) == 1):
                    h = '0' + str(timestamp["hour"])
                if(len(str(timestamp["minute"])) == 1):
                    m = '0' + str(timestamp["minute"])
                if(len(str(timestamp["second"])) == 1):
                    s = '0' + str(timestamp["second"])
                msg = self.process_msg(message)
                self.messages.insert(0, (user, msg[0], color, "<" + h + ":" + m + ":" + s + ">"))
                self.queue(user, msg[1], color, "", True)
            else:
                msg = self.process_msg(message)
                self.messages.insert(0, ("", msg[0], color, ""))
                self.queue(user, msg[1], color, "", True)
        print(self.messages)

    def process_msg(self, message):
        for i in range(self.wordlimit, 0, -1):
            if(message[i] == ' '):
                return (message[:i], message[i+1:])

    # post messages to chatboard
    def write(self):
        im = cv.imread('img.jpg', 1)
        index = 0
        for message in self.messages:
            if len(message[3]) != 0:
                cv.putText(im, message[3] + " " + message[0] + ": " + message[1], (int(im.shape[1]/4), im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            else:
                cv.putText(im, message[0] + message[1], (int(im.shape[1]/4), im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            index += 1
        cv.imwrite(str(self.getPath()) + '.jpg', im)
    
    # queue mqtt topic for chatboard placement
    def queueRoom(self, room, highlighted):
        self.rooms.append((room, highlighted))

    # post message rooms to chatboard
    def writeRooms(self):
        index = 0
        print(self.rooms)
        for room, highlighted in self.rooms:
            cv.putText(im, room, 10, im.shape[0]-80-50*index, cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv.LINE_AA)
            if(highlighted):
                cv.putText(im, room, 10, im.shape[0]-80-50*index, cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv.LINE_AA, thickness = 2)
        cv.imwrite(str(self.getPath()) + '.jpg', im)


if __name__ == '__main__':
    chat1 = ARChat("chat1")
    inputMsg = '{"message_type": "text", "sender": "John", "receiver": "Tyler", "data": "This is the message that will be displayed in AR chat", "time": {"hour": 12, "minute": 31, "second": 22}, "ID": 12345, "color": [255,0,255]}'
    inputMsg1 = '{"message_type": "text", "sender": "Nico", "receiver": "Tyler", "data": "this is a test message", "time": {"hour": 12, "minute": 33, "second": 32}, "ID": 12345, "color": [255,0,0]}'
    inputMsg2 = '{"message_type": "text", "sender": "Michael", "receiver": "Tyler", "data": "this is another test message", "time": {"hour": 12, "minute": 34, "second": 12}, "ID": 12345, "color": [0,0,255]}'
    inputMsg3 = '{"message_type": "text", "sender": "Nate", "receiver": "Tyler", "data": "message", "time": {"hour": 12, "minute": 34, "second": 39}, "ID": 12345, "color": [0,255,255]}'
    inputMsg4 = '{"message_type": "text", "sender": "Tommy", "receiver": "Tyler", "data": "this is an overflowed message that has to be really long to show the overflow functionality built different", "time": {"hour": 1, "minute": 2, "second": 54}, "ID": 12345, "color": [255,255,0]}'

    msg = json.loads(inputMsg)
    msg1 = json.loads(inputMsg1)
    msg2 = json.loads(inputMsg2)
    msg3 = json.loads(inputMsg3)
    msg4 = json.loads(inputMsg4)

    chat1.queue(msg["sender"], msg["data"], msg["color"], msg["time"])
    chat1.queue(msg1["sender"], msg1["data"], msg1["color"], msg1["time"])
    chat1.queue(msg2["sender"], msg2["data"], msg2["color"], msg2["time"])
    chat1.queue(msg3["sender"], msg3["data"], msg3["color"], msg3["time"])
    chat1.queue(msg4["sender"], msg4["data"], msg4["color"], msg4["time"])
    chat1.write()

    """
    chat1.queueRoom("chat1", True)
    chat1.queueRoom("chat2", False)
    chat1.queueRoom("chat3", False)
    chat1.writeRooms(cv.imread('img.jpg', 1), str(chat1.getPath()) + '.jpg')
    """
