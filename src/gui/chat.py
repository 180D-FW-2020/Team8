import mqtt
import chat_image
import numpy as np

EMPTYBOARD = {  
    "topic"     :   str,
    "net"       :   mqtt.MQTTNetObject, 
    "chat"      :   chat_image.ARChat
            }

class BoardManager(QObject):
    update = pyqtSignal(np.ndarray)
    def __init__(self, user, parent=None):
        super().__init__(parent)

        self.boards = [{
            "topic" :   "general",
            "net"   :   mqtt.MQTTNetObject('ece180d/MEAT/general', user, 
                                color = (np.random.rand(), np.random.rand(), np.random.rand()))
            "chat"  :   chat_image.ARChat()
        }]
        self.topic = "general"

    def createBoard(self, **kwargs):
        # to add: implement check that asserts board follows types
        for kw in kwargs:
            board[kw] = kwargs[kw]
        self.boards.append(board)

    def switchTopic(self, topic):
        self.topic = topic
    