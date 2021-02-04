from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class TestStateMachine(QStateMachine):
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent)

        self.fstate = QState()
        super().addState(self.fstate)
        super().setInitialState(self.fstate)
        self.states = []

    def makeState(self, )