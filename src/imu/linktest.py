import mqtt_link as mqtt

def handleIMU(action, mqtt_test):
    mqtt_test.addText(action, "Siri")
    mqtt_test.send()

if __name__ == "__main__":
    mqtt_test = mqtt.MQTTLink("ece180d/MEAT/imu")
    mqtt_test.addText("test test", "Siri")
    mqtt_test.send()
    #handleIMU("test test", mqtt_test)