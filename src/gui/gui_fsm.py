## example code for QStates, QStateMachines, and their workflows

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import time
import sys
sys.path.append('../')
from envrd.audio.audio import *

MAXTIME = 3000

class JobSignals(QObject):
    error = pyqtSignal(tuple) # redirect error reporting
    output = pyqtSignal(object) # notify slot of function returned value
    done = pyqtSignal() # notify main thread of completion
    def __init__(self, parent=None):
        super().__init__(parent)

class JobRunner(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(JobRunner, self).__init__()

        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = JobSignals()

    @pyqtSlot()
    def run(self):
        try:
            output = self.function(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.done.emit()

class DummyObject(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        phrase = {'testing': False}
        self.r = SpeechRecognizer(phrase)

    def doStuff(self):
        self.r.listenForPhrases()


class TimedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QTimer(interval=MAXTIME, singleShot=True)

    def start(self):
        self.timer.start()


class MainWidget(QWidget):
    done1 = pyqtSignal()
    done2 = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.statemachine = QStateMachine()

        self.s1 = QState()

        self.s2 = QState()

        # sequential-child state
        self.s3 = QState()
        self.s31 = QState(self.s3)
        self.s32 = QState(self.s3)
        self.s3f = QFinalState(self.s3)  # must manually enter finalstate
        self.s3.setInitialState(self.s31)

        # parallel-child state
        self.s4 = QState(childMode=1)
        self.s41 = QState(self.s4)
        self.s4f = QFinalState(self.s4) # wait for children to finish; this will be entered automatically
        self.s42 = QState(self.s4)
        # self.s42f = QFinalState(self.s42)

        self.b1 = TimedButton()
        self.dummy = DummyObject()

        self.p = QProgressBar(minimum=0,maximum=MAXTIME)
        self.threadpool = QThreadPool()

        # assignProperty():
        # when state is entered, change a QProperty member of the target var
        # @param
        # arg0: target var
        # arg1: name of QProperty as a str
        # arg2: value of QProperty as desired type
        self.s1.assignProperty(self.b1, "text", "click me")
        self.s2.assignProperty(self.b1, "text", "clicked")
        self.s2.entered.connect(self.worker_state2)
        self.s2.entered.connect(self.b1.start)
        self.s2.entered.connect(self.update_bar)
        self.s3.entered.connect(self.p.reset)
        self.s31.entered.connect(lambda: self.stuff1(self.s31))
        self.s32.entered.connect(lambda: self.stuff2(self.s32))
        self.s41.entered.connect(lambda: self.stuff1(self.s41))
        self.s42.entered.connect(lambda: self.stuff2(self.s42))
        # self.s42.entered.connect(lambda: self.stuffforever(self.s42))

        # addTransition():
        # upon some signal, switch to a different state
        # @param
        # arg0: QObject
        # arg1: signal from QObject
        # arg2: QState to switch to
        self.s1.addTransition(self.b1.clicked, self.s2)

        self.s2.addTransition(self.b1.timer.timeout, self.s3)

        self.s31.addTransition(self.done1, self.s32)
        self.s32.addTransition(self.done2, self.s3f)
        self.s3.addTransition(self.s3.finished, self.s4)

        # self.s41.addTransition(self.done1, self.s4f)
        # self.s42.addTransition(self.done2, self.s4f)
        # self.s42.addTransition(self.done2, self.s42f)
        self.s4.addTransition(self.s4.finished, self.s1)

        self.statemachine.addState(self.s1)
        self.statemachine.addState(self.s2)
        self.statemachine.addState(self.s3)
        self.statemachine.addState(self.s4)
        self.statemachine.setInitialState(self.s1)
        self.statemachine.start()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.b1)
        self.layout.addWidget(self.p)
        self.setLayout(self.layout)

    # NOTE: a signal can be reused within the scope of a state machine without
    #       accidentally triggering more than one slot; only the current state
    #       will process the signal

    # NOTE: QFinalStates are not needed if you manually emit the state's finished signal
    #       inside a function being executed during the state;
    #       however they are VERY PREFERRED
    def stuff1(self, state):
        print('entered substate 1')
        self.done1.emit()

    def stuff2(self, state):
        print('entered substate 2')
        time.sleep(2)
        self.done2.emit()

    def stuffforever(self, state):
        while(1):
            time.sleep(1)

    def print_state(self, state):
        print(state)

    def update_bar(self):
        t = self.b1.timer
        rtime = t.remainingTime()
        while(rtime > 0):
            self.p.setValue(MAXTIME - rtime)
            rtime = t.remainingTime()

    # example thread handler
    # NOTE: commented line has a bug;
    #       if main thread is busy, slot will not execute right after signal is emitted,
    #       because the slot is executed by the main thread.
    #       To avoid this, perform desired actions within the thread.
    #       If you want the slot to execute on state transition AND main thread is not busy
    #       during transition, then use the commented line
    def worker_state2(self):
        if self.threadpool.activeThreadCount() < 1:
            worker = JobRunner(self.dummy.doStuff)
            func = lambda: print("worker finished...")
            worker.signals.done.connect(func)
            self.threadpool.start(worker)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    main_widget = MainWidget()
    window.setCentralWidget(main_widget)
    window.show()
    sys.exit(app.exec_())