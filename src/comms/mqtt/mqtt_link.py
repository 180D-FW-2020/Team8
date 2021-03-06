
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

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MQTTLink(QObject):

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

        # do not receive our own messages
        if not (cur["senderID"] == self.user):
            self.receiveMessage(cur)


    def __init__(self, board, user, color = (255, 255, 255), emoji = "/smileyface", parent=None):
        super().__init__(parent)
        self.tx = mqtt.Client()
        self.rx = mqtt.Client()
        self.board = board
        self.messages = {"acks":[],
                         "messages":[],
                         "senderID": user,
                         "senderColor": color,
                         "senderEmojiImage":emoji
                        }
        self.count = 0
        self.user = user
        self.last_received = {}
        self.network = {}

        self.listen_called = False

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
        if self.listen_called:
            self.rx.loop_stop()
        self.tx.disconnect()
        self.rx.disconnect()

    def __addMessage(self, message_content):
        self.messages["messages"].append(message_content)
        self.count +=1
    
    def __add_ack(self,ID):
        if not (ID in self.messages["acks"]):
            self.messages["acks"].append(ID)

    def __recieve_ack(self, ID):
        for message in self.messages["messages"]:
            if ID == message["ID"]:
                self.messages["messages"].remove(message)
            

    def receiveMessage(self, message):
        # note: there can be multiple messages in the stack recieved
        form_message = ''
        if message["senderID"] not in self.last_recieved:
            self.last_recieved[message["senderID"]]= []
            self.network[message["senderID"]] = {
                                                    "color":message["senderColor"],
                                                    "emoji": message["senderEmojiImage"]
                                                }
        for msg in message["messages"]:
            if (msg["receiver"] == self.user or msg["receiver"] == "all") and (msg["ID"] not in self.last_recieved[message["senderID"]]):
                form_message += msg['sender'] + " said: " + msg['data'] + '\n'

        # recieve acks
        for ack in message["acks"]:
            self.__recieve_ack(ack)

        # add any new acks
        for msg in message["messages"]:
            self.__add_ack(msg["ID"])

        # we can change the contents of form message if another format is more desirable
        if form_message : 
            print(form_message)

        # record message IDss
        IDs = []
        for msg in message["messages"]:
            IDs.append(msg["ID"])
        self.last_recieved[message["senderID"]] = IDs

    def addText(self, text, receiver, emojis = []):
        now = datetime.datetime.now()
        ID = self.board + '_' + self.user + '_' + str(self.count)
        msg = {
            "message_type" : "text",
            "sender" : self.user,
            "receiver" : receiver,
            "data" : text,
            "time" : {
                "hour":now.hour,
                "minute": now.minute,
                "second": now.second
            },
            "ID" : ID, 
            "color": self.messages['senderColor'], 
            "emoji": emojis
        }
        self.__addMessage(msg)

    def addGesture(self, gesture, reciever):
        now = datetime.datetime.now()
        ID = self.board + '_' + self.user + '_' + str(self.count)
        msg = {
            "message_type" : "gesutre",
            "sender" : self.user,
            "reciever" : reciever,
            "data" : gesture,
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
        self.tx.publish(self.board, json.dumps(self.messages), qos=1)
        self.tx.loop_stop()

    def listen(self, duration= -1):
        #only listen if a receiver is initiated
        if duration == -1:
            self.listen_called = True
            self.rx.loop_forever() # changed from loop forever so nonblocking thread
        else:
            self.rx.loop_start()
            time.sleep(duration)
            self.rx.loop_stop()

    #network getter functions
    def getColor(self, user):
        #getter function to return color for a given user
        if user in self.network:
            return self.network[user]["color"]
        else:
            return "white"
            
    def getEmojiTag(self,user):
        # getter function to return emoji for a given user
        if user in self.network:
            return self.network[user]["emoji"]
        else:
            return 0