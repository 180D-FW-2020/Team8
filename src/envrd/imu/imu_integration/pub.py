import paho.mqtt.client as mqtt


class PUBLISHER:
    def __init__(self, topic, message):
        self.topic = topic
        self.message = message

    def connect(self):
        client = mqtt.Client()
        client.connect_async('mqtt.eclipseprojects.io')
        return client
    
    def send(self, in_client):
        in_client.publish(self.topic, self.message, qos=1)