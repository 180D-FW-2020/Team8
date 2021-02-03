from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import audio.audio as audio

class AudioObject(QObject, audio.SpeechRecognizer):
    detected_phrase = pyqtSignal(str)
    transcribed_phrase = pyqtSignal(str)
    error = pyqtSignal()
    def __init__(self, keyphrases : dict, *args, parent=None, **kwargs):
        super().__init__(parent, keyphrases=keyphrases)

    # @desc
    # emits a string containing the most recently transcribed phrase
    def sendCurrentPhrase(self):
        while self.current_phrase == None:
            continue
        self.transcribed_phrase.emit(self.current_phrase)

    def receivePhrase(self):
        print("entered receivePhrase")
        while True:
            time.sleep(0.5)
            try:
                for phrase, found in self.phrases.items():
                    if found == True:
                        self.resetDetection(phrase)
                        self.detected_phrase.emit(phrase)
            except TypeError:
                pass
            except ValueError:
                pass

    def speechHandler(self):
        self.listenForPhrases()