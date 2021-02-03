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

sys.path.append('src/comms/mqtt/')
import mqtt_link as mqtt

mqtt_link_a = mqtt.MQTTLink("ece180d/MEAT/general", "a")
mqtt_link_a.addText("for b", "b")
mqtt_link_a.addText("for everyone", "all")

mqtt_link_a.listen()
while mqtt_link_a.messages["messages"]:
    mqtt_link_a.send()
    time.sleep(1)
mqtt_link_a.send()

time.sleep(1)

input("Press Enter to continue...")
