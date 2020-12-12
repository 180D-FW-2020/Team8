######################################
# File Name : mqtt_message
#
# Author : Thomas Kost
#
# Date: October 24, 2020
#
# Breif : file generalizing sending and recieving of MQTT messages
#
######################################
import json
import mqtt_message as mqtt

# defining for test script
if __name__ == '__main__':

    # Note: make sure you are reading values from a subscriber on the same board to see the result
    
    # Test Rx
    mqtt_rx = mqtt.MQTTLink("rx", "ece180d/MEAT")
    mqtt_rx.listen(20.0)
    print(json.dumps(mqtt_rx.get_message()))