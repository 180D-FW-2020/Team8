from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

## MQTTLink #######################################################################################################
## a class for handling the backend of the messaging system via MQTT

class MQTTLink(QObject):
    '''
    An MQTTLink object can send messages given to it, and receives messages when it is listening

    Public Members:
        - message: a received message that is triggered upon message receive (whatever that means)
    '''
    message = pyqtSignal(dict)

    def __init__(self, topic):
        '''
        Initialize a new MQTTLink object 
        
        Inputs:
            - topic: the topic to which the MQTT link is subscribed
        '''
        pass

    def listen(self):
        '''
        Activates the receiving capabilities of the MQTTLink object, public function to allow
        for threading. 
        
        Inputs:
            - None
        
        Returns:
            - None
        '''
        pass

    def send(self, message):
        '''
        Sends a message or list of messages over the board to which it is subscribed
        
        Inputs:
            - message: a dictionary or list of dictionaries of structure MSG (globals.py)
        
        Returns:
            - None
        '''
        pass

    def __receive__(self):
        '''
        A private function that is called upon receival of a message
        
        Inputs:
            - (#TODO:)
        
        Returns:
            - (#TODO:)
        '''
        message = {}
        self.message.emit(message)