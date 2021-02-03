#
#  File: stop_and_wait_ARQ.py
# 
#  Author: Thomas Kost
#  
#  Date: 01 February 2021
#  
#  @brief This file is used for managing local networks for MQTTLink objects.
#         Note: this is a blank implementation as further functionality is not needed at the moment
#

import mqtt_link as mqtt

class SARQNetwork:
    #used for adding user ID to messages
    def __add_user(self, user):
        pass

    def __init__(self, mqtt_node):
        self.mqtt_node = mqtt_node #can perform TX/RX
        self.network = {} #users
        self.__add_user(self.mqtt_node.user)

    def send(self):
        pass

    def receive(self):
        pass
    
    def add_message(self,text,reciever):
        pass

