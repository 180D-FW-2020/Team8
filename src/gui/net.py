
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys

sys.path.append("src/comms/mqtt")
sys.path.append("src/gui")

import mqtt_net as mqtt

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

class MQTTIMUObject(QObject):
    gestup = pyqtSignal(bool)
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.link = mqtt.MQTTLink('ece180d/MEAT/general/gesture', user_id = user)
        self.user = user
        self.link.message.connect(lambda packet: self.gesture(packet))

    def gesture(self, datapacket):
        print('message received')
        if datapacket['message_type'] == 'gesture':
            word = datapacket['data']
            self.gestup.emit(word == 'up')
        

                     
            