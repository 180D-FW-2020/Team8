### MEAT audio module

import speech_recognition as sr
import time
from queue import Queue

class SpeechRecognizer:
    def __init__(self, keyphrases : dict):
        print("starting audio module...")
        self.recog = sr.Recognizer()
        self.phrases = keyphrases
        audio_queue = Queue()
        with sr.Microphone() as source:
            self.recog.adjust_for_ambient_noise(source)
        self.current_phrase = None

    def recognize():
        while True:
            audio = audio_queue.get()
            if audio == None:
                break
            try:
                out = self.recog.recognize_sphinx(audio)
                print("Sphinx heard: " + out)
                self.current_phrase = out
                for phrase in self.phrases:
                    if phrase in out:
                        self.phrases[phrase] = True
            except sr.UnknownValueError:
                print("Sphinx could not understand audio")
            except sr.RequestError as err:
                print("Sphinx error; {0}".format(err))


    # def listenForPhrases(self):
    #     new_mic = sr.Microphone()
    #     with new_mic as source:
    #         self.recog.adjust_for_ambient_noise(source)
    #     self.stop_listening = self.recog.listen_in_background(new_mic, self._recognize_in_background, phrase_time_limit=5)
    
    def addKeyphrase(self, keyphrase):
        if keyphrase not in self.phrases:
            self.phrases[keyphrase] = False
        else:
            print("phrase {0} already in list, skipping...".format(keyphrase))

    def removeKeyphrase(self, keyphrase):
        if keyphrase in self.phrases:
            self.phrases.pop(keyphrase)
        else:
            print("phrase {0} not already in list, skipping...".format(keyphrase))

    # def _recognize_in_background(self, recognizer, audio):
    #     try:
    #         out = self.recog.recognize_sphinx(audio)
    #         # self.callback()
    #         print("Sphinx heard: " + out)
    #         self.current_phrase = out
    #         for phrase in self.phrases:
    #             if phrase in out:
    #                 self.phrases[phrase] = True
    #         self.receivePhrase()
    #     except sr.UnknownValueError:
    #         print("Sphinx could not understand audio")
    #     except sr.RequestError as err:
    #         print("Sphinx error; {0}".format(err))

    # def receivePhrase(self):
    #     pass

    def resetCurrentPhrase(self):
        self.current_phrase = None

    def resetDetection(self, phrase):
        self.phrases[phrase] = False

    # @desc
    # deprecated, use reset_detection after each detect change
    # def reset_detect_events(self):
    #     self.phrases = dict.fromkeys(self.phrases, False)   

    # def teardown(self):
    #     print("stopping audio module...")
    #     if self.stop_listening != None:
    #         self.stop_listening(wait_for_stop=False)
    #         self.stop_listening = None

    #####################################################
