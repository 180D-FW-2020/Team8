from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json

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

import mqtt_link as mqtt
import stringparser

class MQTTNetObject(QObject, mqtt.MQTTLink):
    receive = pyqtSignal(str)
    emoji = pyqtSignal(list)
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def __parse__(self, message):
        out = parse_string(message, DELIM, EMOTEIDS)
        text = out[0]
        emojis = out[1]

    def receiveMessage(self, message):
        super().receiveMessage(message)
        
        emojis = []
        for msg in message['messages']:
            receive.emit(msg)
            for emote in msg['emoji']:
                emojis.append(emote)
        emoji.emit(emojis)
        
    def sendMessage(self, message):
        msg = self.__parse__(message)
        self.addText(msg['data'], msg['receiver'], msg['emojis'])
        self.send()