##
 #  File: gui.py
 # 
 #  Author: Nate Atkinson
 #  
 #  @brief ui and event handling for data/classifiers
 #

import cv2 as cv
import tkinter as tk
# import hand_tracker
# import static_homography
# import mqtt_message
# import audio

class MQTTNetObject:
    def __init__(self):
        #TODO
        pass

class IMUSampleObject:
    def __init__(self):
        #TODO
        pass

class AreaSelectObject:
    def __init__(self):
        #TODO
        pass

class AudioObject(audio.SpeechRecognizer):
    def __init__(self, keyphrases):
        SpeechRecognizer.__init__(self)
        self.keyphrases = keyphrases
        for phrase in self.keyphrases:
            self.add_keyphrase(self, phrase)


class UI:
    def __init__(self):
        self.MQTTHandler = MQTTNetObject()
        self.IMUSampler = IMUSampleObject()
        self.AreaSelector = AreaSelectObject()

        self.stt_keyphrases = ["testing"] #placeholder, update once default phrases are known
        self.SpeechToText = AudioObject(self.stt_keyphrases)

