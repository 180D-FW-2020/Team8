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
import paho.mqtt.client as mqtt
import time
import datetime


class MQTTLink:

        # MQTT client functions
    def __on_connect_subscriber(self, client, userdata, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.board, qos=1)
    
    def __on_disconnect_subscriber(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')
    
    def __on_connect_publisher(self, client, userdata, flags, rc):
        print("Connection returned result: "+str(rc))

    
    def __on_disconnect_publisher(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')
    
    def __on_message(self, client, userdata, message):
        #filter data to get only json
        #parse message
        self.message["messages"].append(json.loads(str(message.payload)[2:-1]))

    def __init__(self, tx_rx, board ):
        self.tx = (tx_rx == "tx")
        self.rx = (tx_rx == "rx")
        self.client = mqtt.Client()
        self.board = board
        self.message = {"messages" :[]}

        #configure client
        if self.tx: 
            self.client.on_connect = self.__on_connect_publisher
            self.client.on_disconnect = self.__on_disconnect_publisher
            self.client.on_message = self.__on_message
        else :
            self.client.on_connect = self.__on_connect_subscriber
            self.client.on_disconnect = self.__on_disconnect_subscriber
            self.client.on_message = self.__on_message

        self.client.connect_async('mqtt.eclipseprojects.io')

    def __del__(self):
        self.client.disconnect()

    def listen(self, duration= -1):
        #only listen if a reciever is initiated
        if self.rx:
            if duration == -1:
                self.client.loop_forever()
            else:
                self.client.loop_start()
                time.sleep(duration)
                self.client.loop_stop()
            
        else:
            print("Error: not rx")

    def getMessage(self):
        return self.message["messages"]

    def __addMessage(self, message_content):
            self.message["messages"].append(message_content)

    def addText(self, text, receiver, sender):
        now = datetime.datetime.now()
        msg = {
            "message_type" : "text",
            "data" : text,
            "sender" : sender, 
            "receiver" : receiver,
            "time":{

                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            }
        }
        self.__addMessage(msg)

    def addWeather(self, conditions, temp, high, low):
        msg = {
            "message_type" : "weather",
            "data" : {
                "conditions": conditions,
                "temp":temp,
                "high":high,
                "low":low
            }
        }
        self.__addMessage(msg)

    def addNews(self, hyperlink, summary):
        msg = {
            "message_type": "news",
            "data": hyperlink,
            "relevant_text": summary
        }
        self.__addMessage(msg)

    def send(self):
        self.client.loop_start()
        # only send if a transmitter has been initiated
        if self.tx:
            self.client.publish(self.board, json.dumps(self.message), qos=1)
            self.message = {"messages":[]}
        else:
            print("Error: not Tx")
        self.client.loop_stop()
        self.client.disconnect()

