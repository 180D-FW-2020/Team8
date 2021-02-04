import mqtt
import chat_image
import numpy as np
import datetime

EMPTYBOARD = {  
    "topic"     :
    {"net"       :   mqtt.MQTTNetObject, 
    "chat"      :   chat_image.ARChat}
            }

class BoardManager(QObject):
    update = pyqtSignal(np.ndarray)
    def __init__(self, user, parent=None):
        super().__init__(parent)

        self.topic = "ece180d/MEAT/general"
        self.boards = {"ece180d/MEAT/general": 
            {
            "net"       :   mqtt.MQTTNetObject("ece180d/MEAT/general", user, 
                                color = (np.random.rand(), np.random.rand(), np.random.rand()))
            "chat"      :   chat_image.ARChat()
            }
        }

        self.gesturer = mqtt.MQTTIMUObject("ece180d/MEAT/general/gesture", user)
        self.gesturer.gestup.connect(lambda x: self.switchTopic(x))
        

    def createBoard(self, topic:str, net:mqtt.MQTTNetObject, chat:chat_image.ARChat):
        
        net.receive.connect(lambda x: self.receivePost(topic, x))

        new_board = { board     :
                        {"net"   :   net,    
                         "chat"  :   chat}} 
        self.boards.append(new_board)

    def switchTopic(self, forward):
        keys = self.boards.keys()
        idx = keys.index(self.topic)
        if forward:
            try:
                self.topic = keys[idx+1]
            except IndexError:
                self.topic = keys[0]
        else:
            try:
                self.topic = keys[idx-1]
            except IndexError:
                self.topic = keys[len(keys)-1]

        boards[self.topic]["chat"].write()

    def userPost(self, message):
        board = self.boards[self.topic]
        board["net"].sendMessage(message)

        user = board["net"].messages["senderID"]
        color = board["net"].getColor()
        now = datetime.datetime.now()
        time = {
                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            }

        board["chat"].queue(user, message, color, time)
        board["chat"].write()

    def receivePost(self, topic, message):
        board = self.boards[topic]
        user = message['sender']
        color = message['color']
        time = message['time']
        board["chat"].queue(user, message, color, time)

        if self.topic is topic:
            board["chat"].write()

        


