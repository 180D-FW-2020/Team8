# import base_test
import time
import sys
sys.path.append("src/gui")
from speech import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# @desc
# dump all required signals here 
# (likely won't be needed since signals are threadsafe and can be emitted/received outside thread)
class JobSignals(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    error = pyqtSignal(tuple) # redirect error reporting
    output = pyqtSignal(object) # notify slot of function returned value
    done = pyqtSignal() # notify main thread of completion

# @desc
# utility class for handling multithreading in Qt
# all heavy event-triggered ops should be called through this class
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
            return
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.output.emit(output)
        finally:
            self.signals.done.emit()

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.phrases = {'testing': False}
        # widgets and objects
        self.audio = AudioObject(self.phrases)
        
        # signals and slots
        self.audio.detected_phrase.connect(lambda: print("detected phrase"))

        # threading
        self.threadpool = QThreadPool()
        self.__create_worker__(self.audio.speechHandler)

    def keyPressEvent(self, event):
        super(MainWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_Q:
            pass

    def __create_worker__(self, func):
        try:
            worker = JobRunner(func)
            self.threadpool.start(worker)
        except KeyboardInterrupt:
            worker.setAutoDelete(True)

class testUI:
    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.window = QMainWindow()
        self.main_widget = MainWidget()
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    test = testUI()