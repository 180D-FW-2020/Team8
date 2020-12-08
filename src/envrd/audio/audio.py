### MEAT audio module

import speech_recognition as sr
import time

class SpeechRecognizer:
    def __init__(self, keyphrases : dict):
        self.recog = sr.Recognizer()
        self.mic = sr.Microphone()
        self.phrases = keyphrases
        with self.mic as source:
            self.recog.adjust_for_ambient_noise(source)
        self.stop_listening = self.recog.listen_in_background(self.mic, self.recognize_in_background)

    def add_keyphrase(self, keyphrase):
        if keyphrase not in self.phrases:
            self.phrases[keyphrase] = False
        else:
            print("phrase {0} already in list, skipping...".format(keyphrase))

    def remove_keyphrase(self, keyphrase):
        if keyphrase in self.phrases:
            self.phrases.pop(keyphrase)
        else:
            print("phrase {0} not already in list, skipping...".format(keyphrase))

    def recognize_in_background(self, recognizer, audio):
        try:
            out = self.recog.recognize_sphinx(audio)
            print("Sphinx heard: " + out)
            for phrase in self.phrases:
                if phrase in out:
                    self.phrases[phrase] = True
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as err:
            print("Sphinx error; {0}".format(err))

    def reset_detect_events(self):
        self.phrases = dict.fromkeys(self.phrases, False)   

    def teardown(self):
        self.stop_listening(wait_for_stop=False)

