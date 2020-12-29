import mqtt_link as mqtt

# defining for test script
if __name__ == '__main__':
    # Test Rx
    mqtt_rx = mqtt.MQTTLink("ece180d/MEAT/imu")
    mqtt_rx.listen()
