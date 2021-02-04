import mqtt
import chat_image
import numpy as np
import datetime

EMPTYBOARD = {  
    "topic"     :
    {"net"      :   mqtt.MQTTNetObject, 
    "chat"      :   chat_image.ARChat}
            }

class BoardManager(QObject):
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


class BoardFSM:
    def __init__(self, signals, slots):
        self.state_machine = QStateMachine()

        self.s_init = QState() # board not visible
        self.s_main = QState() # board becomes visible here
        self.s_msg = QState()
        self.s_msg_listen = QState(self.s_msg)
        self.s_msg_confirm = QState(self.s_msg)
        self.s_msg_send = QState(self.s_msg)
        self.s_msg.setInitialState(self.s_msg_listen)

        self.state_machine.addState(self.s_init)
        self.state_machine.addState(self.s_main)
        self.state_machine.addState(self.s_msg)
        self.state_machine.setInitialState(self.s_init)

        # signals, slots, and transitions
        self.s_init.entered.connect(slots[0]) # hide chatbox
        self.s_main.entered.connect(slots[1]) # display chatbox
        self.s_msg_listen.entered.connect(slots[2]) # message listen worker
        self.s_msg_send.entered.connect(slots[3]) # send message

        self.s_init.addTransition(signals[0], self.s_main) # 'start chatbox' displays chatbox
        self.s_main.addTransition(signals[1], self.s_msg) # 'send message' enters s_msg_listen
        self.s_main.addTransition(signals[2], self.s_init) # 'close chatbox' hides chatbox
        self.s_msg.addTransition(signals[3], self.s_main) # 'cancel message' backs out of s_msg at any substate
        self.s_msg_listen.addTransition(signals[4], self.s_msg_confirm) # wait until current phrase changes
        self.s_msg_confirm.addTransition(signals[5], self.s_msg_send) # 'yes' sends msg
        self.s_msg_confirm.addTransition(signals[6], self.s_msg_listen) # 'no' returns to listen
        self.s_msg_send.addTransition(self.s_main) # unconditional transition back to main
