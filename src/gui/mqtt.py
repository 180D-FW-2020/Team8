
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import sys

EMOTEIDS = {
    ":/emotes/angry"        : 1 ,
    ":/emotes/cringe"       : 2 ,
    ":/emotes/cry"          : 3 ,
    ":/emotes/doubt"        : 4 ,
    ":/emotes/LOL"          : 5 ,
    ":/emotes/welp"         : 6 ,
    ":/emotes/frown"        : 7 ,
    ":/emotes/grin"         : 8 ,
    ":/emotes/love"         : 9 ,
    ":/emotes/ofcourse"     : 10,           
    ":/emotes/shock"        : 11,
    ":/emotes/simp"         : 12,
    ":/emotes/smile"        : 13,
    ":/emotes/hmmm"         : 14,
    ":/emotes/tongue"       : 15,
    ":/emotes/wink"         : 16
}

DELIM = "slash"

sys.path.append("src/comms/mqtt")
sys.path.append("src/gui")

import mqtt_net as mqtt
import stringparser

class MQTTNetObject(mqtt.MQTTLink):
    receive = pyqtSignal(str)
    emoji = pyqtSignal(list)
    def __init__(self, board, user, color=(0, 0, 0), emoji=None, parent=None):
        super().__init__(board, user, color=color, emoji=emoji, parent=parent)

    def __parse__(self, message):
        out = parse_string(message, DELIM, EMOTEID)
        text = out[0]
        emojis = out[1]

    def receiveMessage(self, message):
        super().receiveMessage(message)
        
        emojis = []
        for msg in message['messages']:
            self.receive.emit(msg)
            for emote in msg['emoji']:
                emojis.append(emote)
        self.emoji.emit(emojis)
        
    def sendMessage(self, message):
        msg = self.__parse__(message)
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
            