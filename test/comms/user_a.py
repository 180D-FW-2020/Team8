#
#  File: user_a.py
# 
#  Author: Thomas Kost
#  
#  Date: 27 January 2021
#  
#  @brief one user with tag "a"
#
import sys
import os
import time
import datetime

sys.path.append('../../src/comms/mqtt/')
sys.path.append('src/comms/mqtt/')
import mqtt_net as mqtt

# Instantiate link
mqtt_link_a = mqtt.MQTTLink("ece180d/MEAT/general", "a",[0,0,0], True)

# Create Messages
now = datetime.datetime.now()
msg_for_b = {
            "message_type" : "text",
            "sender" : "a",
            "receiver" : "b",
            "data" : "for b",
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
            "sender" : "a",
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
mqtt_link_a.listen()
mqtt_link_a.send(msg_for_b)
mqtt_link_a.send(msg_for_all)
while  mqtt_link_a._MQTTLink__data_packet["messages"]:
    mqtt_link_a.send()
    time.sleep(1)
mqtt_link_a.send()

time.sleep(1)

input("Press Enter to continue...")
