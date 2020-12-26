import mqtt_link as mqtt

# defining for test script
if __name__ == '__main__':

    # Note: make sure you are reading values from a subscriber on the same board to see the result
    # Start a client
    mqtt_tx = mqtt.MQTTLink("ece180d/MEAT/general")

    # Add data
    mqtt_tx.addText("very cool messaging Nate!", "user_2")
    
    # Send
    mqtt_tx.send()
