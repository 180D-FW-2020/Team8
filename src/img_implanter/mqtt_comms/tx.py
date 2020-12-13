import json
import mqtt_message as mqtt

# defining for test script
if __name__ == '__main__':

    # Note: make sure you are reading values from a subscriber on the same board to see the result
    # Start a client
    mqtt_tx = mqtt.MQTTLink("tx","ece180d/team8")

    # Add data
    mqtt_tx.addText("some text", "Jack", "John")
    mqtt_tx.addWeather("sunny", 69, 75, 50)
    mqtt_tx.addNews("https://www.youtube.com/watch?v=oHg5SJYRHA0", "important information")
    
    # Send
    mqtt_tx.send()