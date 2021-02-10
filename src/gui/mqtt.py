
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys



sys.path.append("src/comms/mqtt")
sys.path.append("src/gui")

import mqtt
import stringparser

class MQTTNetObject(mqtt.MQTTLink):
    receive = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def __parse__(self, message):
        out = parse_string(message, DELIM, EMOTEID)
        text = out[0]
        emojis = out[1]
        return text, emojis

    def receiveMessage(self, message):
        super().receiveMessage(message)
        
        emojis = []
        for msg in message['messages']:
            self.receive.emit(msg)
            for emote in msg['emoji']:
                emojis.append(emote)
        self.emoji.emit(emojis)
        
    def send(self, message):
        message = self.__parse__(message)
        self.addText(msg['data'], msg['receiver'], msg['emojis'])
        self.send()



class MQTTIMUObject(mqtt.MQTTLink):
    gestup = pyqtSignal(bool)
    def __init__(self, board, user, color=(0, 0, 0), emoji=None, parent=None):
        super().__init__(board, user, color=color, emoji=emoji, parent=parent)

    def receiveMessage(self, message):
        super().receiveMessage(message)
        
        for msg in message['messages']:
            if msg["message_type"] is "gesture":
                if msg["data"] is "up":
                    self.gestup.emit(True)
                elif msg["data"] is "down":
                    self.gestup.emit(False)
        

                     
            