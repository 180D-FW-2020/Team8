## AR Chat #######################################################################################################
## a class for creating a message board in OpenCV

ROOT = "data/gui/"

import cv2 as cv


'''
An ARChat object outputs an array with a custom UI created by the Butcher Bros (spec. Michael) 
Public Functions:
    - post: posts a message to the ARChat
    - stage: stages a message to the user's staging area  
    - getPath: returns the path to the ARChat image   
'''
class ARChat():

    '''
    Initialize a new ARChat.
    The ARChat always initializes with at least one board topic, "general"
    
    Inputs:
        - topic: the topic associated with each ARChat
        - roomIndex: number signifying which chatroom in the list of chatrooms is currently selected
        - chatrooms: a list of type str, which contains a string of currently active boards
    
    '''
    def __init__(self, topic, roomIndex, chatrooms = []):
        self.topic = topic
        self.messages = []
        self.rooms = chatrooms
        self.roomIndex = roomIndex
        self.wordlimit = 42
        self.fontSize = 1.5
        self.boardpath = topic
        self.stagedMessage = ""

        self.write_messages()
        self.write_rooms()


    '''
    Posts a message to be updated to the currently active board
    Inputs:
        - user (str): the name of the user who sent the message
        - message (str): the message sent by the user
        - color (tuple): the RGB tuple associated with the user
        - time (dict): dictionary with hour, minute, second
    '''
    def post(self, user, message, color, timestamp, overflow=False):
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
            self.write_messages()
            self.write_rooms()
            self.write_staged_message()
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
                msg = self.process_msg(message, self.wordlimit)
                self.messages.insert(0, (user, msg[0], color, "<" + h + ":" + m + ":" + s + ">"))
                self.post(user, msg[1], color, "", True)
            else:
                msg = self.process_msg(message, self.wordlimit)
                self.messages.insert(0, ("", msg[0], color, ""))
                self.post(user, msg[1], color, "", True)


    '''
    Stages a message to the user's staging area
    
    Inputs:
        - message (str): the string to place in the user's message box
    '''
    def stage(self, message, index=0):
        if(len(message) <= (self.wordlimit + 20)):
            self.stagedMessage = message
            if(index == 0):
                self.write_staged_message()
            else:
                self.write_staged_message(index)
        else:
            msg = self.process_msg(message, self.wordlimit + 20)
            self.stagedMessage = msg[0]
            self.write_staged_message()
            index += 1
            self.stage(msg[1], index)


    '''
    Returns a path to the saved ARChat .png
    '''
    def getPath(self):
        return self.boardpath

    def addRoom(self, topic):
        self.rooms.append(topic)
        self.write_messages()
        self.write_rooms()

    # message overflow processing
    def process_msg(self, message, lim):
        for i in range(lim, 0, -1):
            if(message[i] == ' '):
                return (message[:i], message[i+1:])

    # post messages to chatboard
    def write_messages(self):
        im = cv.imread(ROOT + 'chat.png', 1)

        index = 0
        for message in self.messages:
            if len(message[3]) != 0:
                cv.putText(im, message[3] + " " + message[0] + ": " + message[1], (int(im.shape[1]/4), im.shape[0]-200-80*index), cv.FONT_HERSHEY_SIMPLEX, self.fontSize, message[2], 2, cv.LINE_AA)
            else:
                cv.putText(im, message[0] + message[1], (int(im.shape[1]/4), im.shape[0]-200-80*index), cv.FONT_HERSHEY_SIMPLEX, self.fontSize, message[2], 2, cv.LINE_AA)
            index += 1
        cv.imwrite(str(self.getPath()) + '.png', im)

    # post message rooms to chatboard
    def write_rooms(self):
        im = cv.imread(str(self.getPath()) + '.png', 1)
        index = 0
        for room in self.rooms:
            cv.putText(im, room, (50, im.shape[0]-1000+100*index), cv.FONT_HERSHEY_SIMPLEX, self.fontSize, (255,255,255), 2, cv.LINE_AA)
            if(index == self.roomIndex):
                cv.putText(im, room, (50, im.shape[0]-1000+100*index), cv.FONT_HERSHEY_SIMPLEX, self.fontSize, (255,0,255), 20, cv.LINE_AA)
                cv.putText(im, room, (50, im.shape[0]-1000+100*index), cv.FONT_HERSHEY_SIMPLEX, self.fontSize, (255,255,255), 2, cv.LINE_AA)
            index += 1
        cv.imwrite(str(self.getPath()) + '.png', im)

    # post queued message to chatboard
    def write_staged_message(self, index=0):
        im = cv.imread(str(self.getPath()) + '.png', 1)
        cv.putText(im, self.stagedMessage, (int(im.shape[1]/4), im.shape[0]-90+50*index), cv.FONT_HERSHEY_SIMPLEX, self.fontSize, [255,255,255], 2, cv.LINE_AA)
        cv.imwrite(str(self.getPath()) + '.png', im)

if __name__ == '__main__':
    masterRooms = ["chat1", "chat2", "chat3"]
    chat1 = ARChat("chat1", 0, masterRooms)
    chat2 = ARChat("chat2", 1, masterRooms)
    chat3 = ARChat("chat3", 2, masterRooms)

    chat1.post("Nico", "this is a tester message", [255,124,255], {"hour": 12, "minute": 31, "second": 22})
    chat1.post("Nate", "this is a tester message really long please overflow due to character count", [0,0,255], {"hour": 12, "minute": 32, "second": 11})
    chat1.post("Tommy", "this is a tester message again", [255,0,0], {"hour": 12, "minute": 33, "second": 1})
    chat1.stage("I don't think this overflow works as intended yet so why don't I keep testing this stuff and see when it breaks")

    chat2.post("Michael", "testing testing 123", [0,255,0], {"hour": 1, "minute": 5, "second": 2})
    
    chat3.post("Walter", "Let's cook", [125,125,255], {"hour": 1, "minute": 5, "second": 2})
    chat3.post("Jesse", "Hell yeah", [255,125,125], {"hour": 1, "minute": 5, "second": 56})