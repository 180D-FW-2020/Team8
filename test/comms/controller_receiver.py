#
#  File: controller_receiver.py
# 
#  Author: Thomas Kost
#  
#  Date: 04 February 2021
#  
#  @brief  receives controller data for a generic user
#

import sys
import os
import time

sys.path.append('../../src/comms/mqtt/')
sys.path.append('src/comms/mqtt/')
import mqtt_net as mqtt

mqtt_link = mqtt.MQTTLink("ece180d/MEAT/general/gesture", "my_name",[0,0,0], True)
mqtt_link.listen()

while(True):
    mqtt_link.send()
    time.sleep(1)

time.sleep(1)

input("Press Enter to continue...")
#ece180d/MEAT/general/gesture
