import cv2 as cv
import json

class ARChat():
    def __init__(self, path):
        self.messages = []
        self.rooms = []
        self.roomIndex = 0
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

    def process_msg(self, message):
        for i in range(self.wordlimit, 0, -1):
            if(message[i] == ' '):
                return (message[:i], message[i+1:])

    def write(self):
        self.write_messages()
        self.write_rooms()

    # post messages to chatboard
    def write_messages(self):
        im = cv.imread('img.jpg', 1)
        index = 0
        for message in self.messages:
            if len(message[3]) != 0:
                cv.putText(im, message[3] + " " + message[0] + ": " + message[1], (int(im.shape[1]/4), im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            else:
                cv.putText(im, message[0] + message[1], (int(im.shape[1]/4), im.shape[0]-80-50*index), cv.FONT_HERSHEY_SIMPLEX, 1, message[2], 2, cv.LINE_AA)
            index += 1
        cv.imwrite(str(self.getPath()) + '.jpg', im)
    
    def getRooms(self, rooms):
        return self.rooms

    # set rooms for chatboard placement
    def setRooms(self, rooms, index):
        self.rooms = rooms
        self.roomIndex = index

    # post message rooms to chatboard
    def write_rooms(self):
        im = cv.imread(str(self.getPath()) + '.jpg', 1)
        index = 0
        for room in self.rooms:
            cv.putText(im, room, (50, im.shape[0]-1000+100*index), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv.LINE_AA)
            if(index == self.roomIndex):
                cv.putText(im, room, (50, im.shape[0]-1000+100*index), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 20, cv.LINE_AA)
                cv.putText(im, room, (50, im.shape[0]-1000+100*index), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv.LINE_AA)
            index += 1
        cv.imwrite(str(self.getPath()) + '.jpg', im)


if __name__ == '__main__':
    # FIRST CHAT
    chat1 = ARChat("chat1")
    inputMsg = '{"message_type": "text", "sender": "John", "receiver": "Tyler", "data": "This is the message that will be displayed in AR chat", "time": {"hour": 12, "minute": 31, "second": 22}, "ID": 12345, "color": [255,124,255]}'
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

    masterRooms = ["chat1", "chat2", "chat3"]

    chat1.setRooms(masterRooms, 0)
    chat1.write()

    # SECOND CHAT
    chat2 = ARChat("chat2")
    chat2msg1 = '{"message_type": "text", "sender": "Chris", "receiver": "Tyler", "data": "This is the message that will be displayed in AR chat", "time": {"hour": 8, "minute": 3, "second": 1}, "ID": 12345, "color": [255,124,255]}'
    chat2msg2 = '{"message_type": "text", "sender": "Jesus", "receiver": "Tyler", "data": "this is a test message", "time": {"hour": 9, "minute": 42, "second": 12}, "ID": 12345, "color": [255,0,0]}'

    m1 = json.loads(chat2msg1)
    m2 = json.loads(chat2msg2)

    chat2.queue(m1["sender"], m1["data"], m1["color"], m1["time"])
    chat2.queue(m2["sender"], m2["data"], m2["color"], m2["time"])

    chat2.setRooms(masterRooms, 1)
    chat2.write()

