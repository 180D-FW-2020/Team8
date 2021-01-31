### MEAT audio module

import speech_recognition as sr
import time

class SpeechRecognizer:
    def __init__(self, keyphrases : dict):
        print("starting audio module...")
        self.recog = sr.Recognizer()
        self.phrases = keyphrases
        self.current_phrase = None # entire sentence
        self.audio_source = sr.Microphone()
        with self.audio_source as source:
            self.recog.adjust_for_ambient_noise(source)

    def _recognize(self, audio):
        try:
            out = self.recog.recognize_sphinx(audio)
            print("Sphinx heard: " + out)
            self.current_phrase = out
            for phrase in self.phrases:
                if phrase in out:
                    print("phrase found")
                    self.phrases[phrase] = True
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as err:
            print("Sphinx error; {0}".format(err))

    def listenForPhrases(self):
        with self.audio_source as source:
            try:
                while True:
                    self._recognize(self.recog.listen(source))
            except KeyboardInterrupt:
                pass

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

    def resetCurrentPhrase(self):
        self.current_phrase = None

    def resetDetection(self, phrase):
        self.phrases[phrase] = False
