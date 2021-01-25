######################################
# File Name : mqtt_message
#
# Author : Thomas Kost, some edits by Nico
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
import queue


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
        cur = json.loads(str(message.payload)[2:-1])
        self.receiveMessage(cur)


    def __init__(self, board, user):
        self.tx = mqtt.Client()
        self.rx = mqtt.Client()
        self.board = board
        self.messages = {"acks":[],
                         "messages":[]
                        }
        self.count = 0
        self.user = user

        #configure client
        # configure transmission
        self.tx.on_connect = self.__on_connect_publisher
        self.tx.on_disconnect = self.__on_disconnect_publisher

        # configure reception
        self.rx.on_connect = self.__on_connect_subscriber
        self.rx.on_disconnect = self.__on_disconnect_subscriber
        self.rx.on_message = self.__on_message

        self.tx.connect_async('mqtt.eclipseprojects.io')
        self.rx.connect_async('mqtt.eclipseprojects.io')

    def __del__(self):
        self.tx.disconnect()
        self.rx.disconnect()

    def __addMessage(self, message_content):
        self.messages[message_content["ID"]] = message_content
        #self.messages.put(message_content)
    
    def __add_ack(self,ID):
       self.messages["acks"].append(ID)

    def __recieve_ack(self, ID):
        for ack in self.messages["acks"]:
            if ID == ack:
                self.messages["acks"].remove(ack) # does assume no repeats but each message should have a unique id
                for message in self.messages["messages"]:
                    if ID == message.ID:
                        self.messages["messages"].remove(

    def receiveMessage(self, message):
        # note: there can be multiple messages )in the stack recieved
        form_message = message['sender'] + " said: " + message['data']
        
        # recieve acks
        for ack in message["acks"]:
            self.__recieve_ack(ack)

        # add any new acks

         

        print(form_message)
    
    def addText(self, text, reciever):
        now = datetime.datetime.now()
        ID = self.board + '_' + self.user + '_' + str(self.count)
        msg = {
            "message_type" : "text",
            "sender" : self.user,
            "reciever" : reciever,
            "data" : text,
            "time" : {
                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            },
            "ID" : ID
        }
        self.__addMessage(msg)

    
    def send(self):
        self.tx.loop_start()

        # just toss it all out there
        while not self.messages.empty():
            next_message = self.messages.get()
            print(next_message)
            self.tx.publish(self.board, json.dumps(next_message), qos=1)

        self.tx.loop_stop()

    def listen(self, duration= -1):
        #only listen if a reciever is initiated
        if duration == -1:
            self.rx.loop_forever()
        else:
            self.rx.loop_start()
            time.sleep(duration)
            self.rx.loop_stop()
            

    