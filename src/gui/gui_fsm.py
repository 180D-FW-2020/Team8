## example code for QStates, QStateMachines, and their workflows

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import time
import sys

MAXTIME = 3000

class TimedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QTimer(interval=MAXTIME, singleShot=True)

    def start(self):
        self.timer.start()


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.statemachine = QStateMachine()
        self.s1 = QState()
        self.s2 = QState()
        self.b1 = TimedButton()
        self.p = QProgressBar(minimum=0,maximum=MAXTIME)

        # assignProperty():
        # when state is entered, change a QProperty member of the target var
        # @param
        # arg0: target var
        # arg1: name of QProperty as a str
        # arg2: value of QProperty as desired type
        self.s1.assignProperty(self.b1, "text", "click me")
        self.s2.assignProperty(self.b1, "text", "clicked")
        self.s2.entered.connect(self.b1.start)
        self.s2.entered.connect(self.update_bar)
        self.s1.entered.connect(self.p.reset)
        # self.s1.entered.connect(lambda: self.print_state('current: s1'))
        # self.s2.entered.connect(lambda: self.print_state('current: s2'))

        # addTransition():
        # upon some signal, switch to a different state
        # @param
        # arg0: QObject
        # arg1: signal from QObject
        # arg2: QState to switch to
        self.s1.addTransition(self.b1.clicked, self.s2)
        self.s2.addTransition(self.b1.timer.timeout, self.s1)

        self.statemachine.addState(self.s1)
        self.statemachine.addState(self.s2)
        self.statemachine.setInitialState(self.s1)
        self.statemachine.start()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.b1)
        self.layout.addWidget(self.p)
        self.setLayout(self.layout)

    def print_state(self, state):
        print(state)

    def update_bar(self):
        t = self.b1.timer
        rtime = t.remainingTime()
        while(rtime > 0):
            self.p.setValue(MAXTIME - rtime)
            rtime = t.remainingTime()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    main_widget = MainWidget()
    window.setCentralWidget(main_widget)
    window.show()
    sys.exit(app.exec_())