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

sys.path.append('src/comms/mqtt/')
import mqtt_link as mqtt

mqtt_link_b = mqtt.MQTTLink("ece180d/MEAT/general", "b")
mqtt_link_b.addText("for a", "a")
mqtt_link_b.addText("for everyone", "all")

mqtt_link_b.listen()
while mqtt_link_b.messages["messages"]:
    mqtt_link_b.send()
    time.sleep(0.1)
mqtt_link_b.send()

time.sleep(1)

input("Press Enter to continue...")
