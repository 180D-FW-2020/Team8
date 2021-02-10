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
        print("Connection returned result: "+str(rc))
    
    def __on_disconnect_publisher__(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    def __on_message__(self, client, userdata, message):
        self.__receive__(message)

    def __init__(self, topic : str, parent=None):
        '''
        Initialize a new MQTTLink object 
        
        Inputs:
            - topic: the topic to which the MQTT link is subscribed
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

    def __del__(self):
        self.tx.disconnect()
        self.rx.disconnect()

    def __receive__(self, message):
        '''
        A private function that is called upon receival of a message
        
        Inputs:
            - message: a received json string
        '''
        msg = json.loads(message)
        print('got: ', msg)
        self.message.emit(msg)

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
            self.rx.loop_forever() # changed from loop forever so nonblocking thread
        else:
            self.rx.loop_start()
            time.sleep(duration)
            self.rx.loop_stop()
        

    def send(self, message):
        '''
        Sends a message or list of messages over the board to which it is subscribed
        
        Inputs:
            - message: a dictionary or list of dictionaries of structure MSG (globals.py)
        
        Returns:
            - None
        '''            
        self.tx.loop_start()
        if isinstance(message, list):
            for msg in message:
                self.tx.publish(self.topic, json.dumps(msg), qos=1)
        elif isinstance(message, dict):
            self.tx.publish(self.topic, json.dumps(message), qos=1)
        else:
            raise TypeError('Unknown message type not supported; try formatting to dictionary')

        self.tx.loop_stop()

    