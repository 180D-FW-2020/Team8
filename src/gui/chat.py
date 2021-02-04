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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.boards = []
        self.topic = ''

    

    def createBoard(self, **kwargs):
        # to add: implement check that asserts board follows types
        board = EMPTYBOARD
        for kw in kwargs:
            board[kw] = kwargs[kw]
        self.boards.append(board)

    def switchTopic(self, topic):
        self.topic = topic
    