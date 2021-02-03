import base_test
from src.envrd.audio.audio import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

phrases = {'testing': False}
rec = SpeechRecognizer(phrases)

rec.listenForPhrases()
