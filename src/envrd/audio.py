    ### MEAT audio module

import speech_recognition as sr
import time

class SpeechRecognizer:
    def __init__(self, keyphrases : dict):
        print("starting audio module...")
        self.recog = sr.Recognizer()
        self._phrases = keyphrases
        self.current_phrase = None # entire sentence
        self.audio_source = sr.Microphone()
        with self.audio_source as source:
            self.recog.adjust_for_ambient_noise(source)

    def emitPhrase(self, phrase):
        pass

    def _recognize(self, audio):
        try:
            out = self.recog.recognize_google(audio)
            print("STT heard: " + out)
            self.current_phrase = out
            for phrase in self._phrases:
                if phrase in out:
                    print("phrase found")
                    self._phrases[phrase] = True
                    self.emitPhrase(phrase)
        except sr.UnknownValueError:
            print("STT could not understand audio")
        except sr.RequestError as err:
            print("STT error; {0}".format(err))

    def listenForPhrases(self):
        with self.audio_source as source:
            while True:
                self._recognize(self.recog.listen(source))
        print("audio teardown")

    def addKeyphrase(self, keyphrase):
        if keyphrase not in self._phrases:
            self._phrases[keyphrase] = False
        else:
            print("phrase {0} already in list, skipping...".format(keyphrase))

    def removeKeyphrase(self, keyphrase):
        if keyphrase in self._phrases:
            self._phrases.pop(keyphrase)
        else:
            print("phrase {0} not already in list, skipping...".format(keyphrase))

    def resetCurrentPhrase(self):
        self.current_phrase = None

    def resetDetection(self, phrase):
        self._phrases[phrase] = False
