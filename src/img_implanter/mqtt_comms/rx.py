import json
import mqtt_message as mqtt

# defining for test script
if __name__ == '__main__':
    # Test Rx
    mqtt_rx = mqtt.MQTTLink("rx", "ece180d/team8")
    mqtt_rx.listen(20.0)
    print(json.dumps(mqtt_rx.get_message()))