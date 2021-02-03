from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json

import mqtt_link as mqtt

class MQTTNetObject(QObject, mqtt.MQTTLink):
    message = pyqtSignal(str)
    emoji = pyqtSignal(int)
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def receiveMessage(self, message):
        super().receiveMessage(message)
        self.new_message.emit(json.dumps(self.last_received))
        emoji = self.get_Emoji_Tag()
        if emoji:
            self.emoji.emit(emoji)

        
    def sendMessage(self, message, receiver):
        self.addText(message, receiver)
        self.send()