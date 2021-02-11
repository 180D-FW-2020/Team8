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
import threading
print(os.getcwd())

sys.path.append('../../src/comms/mqtt/')
sys.path.append('src/comms/mqtt/')
import mqtt_net as mqtt

mqtt_link_a = mqtt.MQTTLink("ece180d/MEAT/general", "a",[0,0,0], True)
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

#listen_thread = threading.Thread(target=mqtt_link_a.listen, args=())
#listen_thread.start()

mqtt_link_a.listen()
mqtt_link_a.send(msg_for_b)
mqtt_link_a.send(msg_for_all)
while  mqtt_link_a._MQTTLink__data_packet["messages"]:
    #print("here")
    mqtt_link_a.send()
    time.sleep(1)
mqtt_link_a.send()


time.sleep(1)

input("Press Enter to continue...")
