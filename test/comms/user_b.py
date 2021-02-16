#
#  File: user_b.py
# 
#  Author: Thomas Kost
#  
#  Date: 27 January 2021
#  
#  @brief testing file creating mqtt user with tag "b" 
#

import sys
import os
import time
import datetime
import threading

sys.path.append('../../src/comms/mqtt/')
sys.path.append('src/comms/mqtt')

import mqtt_net as mqtt

# Instantiate link
mqtt_link_b = mqtt.MQTTLink("ece180d/MEAT/general", "b",[0,0,0], True)

# Create Messages
now = datetime.datetime.now()
msg_for_a = {
            "message_type" : "text",
            "sender" : "b",
            "receiver" : "a",
            "data" : "for a",
            "time" : {
                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            },
            "color": [0,0,0], 
            "emoji": None
        }
msg_for_all = {
            "message_type" : "text",
            "sender" : "b",
            "receiver" : "all",
            "data" : "for all",
            "time" : {
                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            },
            "color": [0,0,0], 
            "emoji": None
        }

# Send and recieve messages until empty queue
mqtt_link_b.listen()
mqtt_link_b.send(msg_for_a)
mqtt_link_b.send(msg_for_all)
while mqtt_link_b._MQTTLink__data_packet["messages"]:
    mqtt_link_b.send()
    time.sleep(0.1)
mqtt_link_b.send()

time.sleep(1)

input("Press Enter to continue...")
