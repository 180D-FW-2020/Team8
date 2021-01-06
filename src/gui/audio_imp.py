from PyQt5.QtCore import *

import time
import sys

PATH = '../envrd/audio'
sys.path.append(PATH)

from audio import audio

class AudioObject(QObject, audio.SpeechRecognizer):
    detected_phrase = pyqtSignal(str)
    transcribed_phrase = pyqtSignal(str)
    error = pyqtSignal()
    def __init__(self, keyphrases : dict, *args, parent=None, **kwargs):
        super().__init__(parent, keyphrases=keyphrases)

    # @desc
    # emits a string containing the most recently transcribed phrase
    def sendCurrentPhrase(self):
        s = self.current_phrase
        if s != None:
            self.transcribed_phrase.emit(s)
            return
        else:
            time.sleep(1)
            self.sendCurrentPhrase()

    def receivePhrase(self):
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
