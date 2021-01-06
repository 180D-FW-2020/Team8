from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import numpy as np

PATH = [
    '../comms/mqtt',
    '../imgproc'
]

for lib in PATH:
    sys.path.append(lib)

import mqtt_link as mqtt
import message_placer as placer

## MQTT QObject Class #######################################################################################################
## QObject connector for MQTT stuff
class MQTTNetObject(QObject, mqtt.MQTTLink):
    new_message = pyqtSignal(str)
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def receiveMessage(self, message):
        form_message = message['sender'] + ": " + message['data']
        self.new_message.emit(form_message)
        
    def sendMessage(self, message, sender):
        self.addText(message, sender)
        self.send()

## Message Board Class #######################################################################################################
## takes in data from a general MQTT board and places it in UI, also takes in user input to send messages
class MessageBoard(QWidget):
    board_image = pyqtSignal(np.ndarray)
    def __init__(self, username='xxxx', num_lines=5, parent=None):
        super().__init__(parent)
        # get an MQTT link
        self.messenger = MQTTNetObject(board="ece180d/MEAT/general")
        self.board_shape = (200, 200)
        self.placer = placer.BoardPlacer(self.board_shape, "br", num_lines)

        # set up message reading
        self.num_lines = num_lines
        self.user_message = {"username":username, "message":"", "state_phrase":""}

        # update message list upon new message
        self.messenger.new_message.connect(lambda message: self.__update_messages(message))

    def __update_messages(self, new_message):
        # append messages so that the last message printed is at bottom
        self.placer.updateChatBoard(new_message)

    def listenUserMessage(self):
        # self.user_message["state_phrase"] = "      Listening..."
        self.placer.updateUserBoard(self.user_message.values())

    def confirmUserMessage(self, message):
        self.user_message["message"] = message
        self.user_message["state_phrase"] = "      Send this message?"
        self.placer.updateUserBoard(self.user_message.values())

    def sendUserMessage(self):
        self.messenger.sendMessage(self.user_message["message"], self.user_message["username"])
        self.user_message["message"] =  ""
        self.user_message["state_phrase"] =  ""
        self.placer.updateUserBoard(self.user_message.values())

    def placeBoard(self, frame):
        frame = self.placer.placeBoard(frame)
        self.board_image.emit(frame)

    def receive(self):
        self.messenger.listen()