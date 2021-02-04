from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json

import mqtt_link as mqtt

class MQTTNetObject(QObject, mqtt.MQTTLink):
    receive = pyqtSignal(str)
    emoji = pyqtSignal(list)
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def __parse__(self, message):


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