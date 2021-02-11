from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import time
from paho.mqtt.client import * 

## MQTTLink #######################################################################################################
## a class for handling the backend of the messaging system via MQTT

class MQTTLink(QObject):
    '''
    An MQTTLink object can send messages given to it, and receives messages when it is listening

    Public Members:
        - message: a received message that is triggered upon message receive 
    '''
    message = pyqtSignal(dict)

    ## Privates #######################################################################################################

    # MQTT client functions
    def __on_connect_subscriber__(self, client, userdata, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.topic, qos=1)
    
    def __on_disconnect_subscriber__(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')
    
    def __on_connect_publisher__(self, client, userdata, flags, rc):
        print("Connection returned result: " + str(rc))
    
    def __on_disconnect_publisher__(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    def __on_message__(self, client, userdata, message):
        self.__receive__(str(message.payload)[2:-1])

    def __init__(self, topic : str, user_id : str, color : list = [255,255,255], debug = True , parent=None):
        '''
        Initialize a new MQTTLink object 
        
        Inputs:
            - topic: the topic to which the MQTT link is subscribed
            - user_id: id tag of the user this link is associated with
            - color: RGB value user text will be shown in
            - debug: boolean enabling print statements
        '''
        super().__init__(parent)
        self.tx = Client()
        self.rx = Client()
        self.topic = topic

        #configure client
        # configure transmission
        self.tx.on_connect = self.__on_connect_publisher__
        self.tx.on_disconnect = self.__on_disconnect_publisher__

        # configure reception
        self.rx.on_connect = self.__on_connect_subscriber__
        self.rx.on_disconnect = self.__on_disconnect_subscriber__
        self.rx.on_message = self.__on_message__

        self.tx.connect_async('mqtt.eclipseprojects.io')
        self.rx.connect_async('mqtt.eclipseprojects.io')

        # Configure Network Paramaters
        self.__data_packet = {  "acks":[],
                                "messages":[],
                                "senderID": user_id,
                                "senderColor": color
                                }
        self.__message_id_count = 0
        self.__user = user_id 

        # the following paramaters are gleaned form the reciept of messages
        self.__last_received_msg_IDS ={} # {"USERID": [ID1,ID2,ID3]} 
        self.__network_users = {} # {"USERID": {"color":[0,0,0],
                                  #             "emoji": "some_tag"}}
        self.__debug = debug


    def __del__(self):
        self.tx.disconnect()
        self.rx.disconnect()

    def __addMessage__(self, message_content):
        '''
        A private function to add a passed in message to our data packet. This handles the addition of
        a unique message ID tag

        Inputs:
            - message content : dictionary of form MSG without an ID tag
        '''
        ID = self.topic + '_' + self.__user + '_' + str(self.__message_id_count)
        message_content["ID"] = ID
        self.__data_packet["messages"].append(message_content)
        self.__message_id_count += 1

    def __add_ack__(self,ID):
        '''
        A private function that handles the adding of acknowledgements to send to other users

        Inputs:
            - ID: outgoing acknowledgement tag 
        '''
        if not (ID in self.__data_packet["acks"]):
            self.__data_packet["acks"].append(ID)

    def __recieve_ack__(self, ID):
        '''
        A private function that handles the recipt of acknoledgements from other users

        Inputs:
            - ID: acknowledgement tag 
        '''
        for message in self.__data_packet["messages"]:
            if ID == message["ID"]:
                self.__data_packet["messages"].remove(message)
    
    def __receive__(self, message):
        '''
        A private function that is called upon receival of a message
        
        Inputs:
            - message: a received json string
        '''
        packet = json.loads(message) # note: there can be multiple messages in the packet recieved
        if packet["senderID"] != self.__user:
            if packet["senderID"] not in self.__last_received_msg_IDS:
                self.__last_received_msg_IDS[packet["senderID"]]= []
                self.__network_users[packet["senderID"]] = {
                                                            "color":packet["senderColor"],
                                                            "emoji": packet["senderEmojiImage"]
                                                        }
            for msg in packet["messages"]:
                if self.__debug:  
                    print(msg["sender"], " said: ", msg["data"])
                self.message.emit(msg)
    
            # recieve acks
            for ack in packet["acks"]:
                self.__recieve_ack__(ack)
    
            # add any new acks
            for msg in packet["messages"]:
                self.__add_ack__(msg["ID"])
    
            # record message IDs
            IDs = []
            for msg in packet["messages"]:
                IDs.append(msg["ID"])
            self.__last_received_msg_IDS[packet["senderID"]] = IDs

    ## Public #######################################################################################################
        
    def listen(self, duration = -1):
        '''
        Activates the receiving capabilities of the MQTTLink object, public function to allow
        for threading. 
        
        Inputs:
            - duration: the duration of the listening in seconds; if -1, listens indefinitely
        
        Returns:
            - None
        '''
        if duration == -1:
            self.listen_called = True
            self.rx.loop_start() # changed from loop forever so nonblocking thread
        else:
            self.rx.loop_start()
            time.sleep(duration)
            self.rx.loop_stop()
        

    def send(self, message : dict = {}):
        '''
        Sends a message or list of messages over the board to which it is subscribed
        
        Inputs:
            - message: a dictionary or list of dictionaries of structure MSG (globals.py)
        
        Returns:
            - None
        '''            

        self.tx.loop_start()
        if message:
            if isinstance(message, list):
                for msg in message:
                    self.__addMessage__(msg)
            elif isinstance(message, dict):
                self.__addMessage__(message)
            else:
                raise TypeError('Unknown message type not supported; try formatting to dictionary')
        self.tx.publish(self.topic, json.dumps(self.__data_packet), qos=1)
        self.tx.loop_stop()

    