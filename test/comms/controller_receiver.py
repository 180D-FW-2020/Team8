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

sys.path.append('src/comms/mqtt/')
import mqtt_link as mqtt

mqtt_link = mqtt.MQTTLink("ece180d/MEAT/general/gesture", "my_name")
while(True):
    mqtt_link.listen()
    mqtt_link.send()

time.sleep(1)

input("Press Enter to continue...")
