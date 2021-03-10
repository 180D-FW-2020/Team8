from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

sys.path.append("src/envrd")
import audio

class AudioObject(QObject, audio.SpeechRecognizer):
    detected_phrase = pyqtSignal(str)
    transcribed_phrase = pyqtSignal(str)
    error = pyqtSignal()
    def __init__(self, keyphrases : dict, *args, parent=None, **kwargs):
        super().__init__(parent, keyphrases=keyphrases)
        print("audio init")

    def emitPhrase(self, phrase):
        self.detected_phrase.emit(phrase)

    # @desc
    # emits a string containing the most recently transcribed phrase
    def sendCurrentPhrase(self):
        while self.current_phrase == None:
            continue
        self.transcribed_phrase.emit(self.current_phrase)

    def speechHandler(self):
        self.listenForPhrases()
