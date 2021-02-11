import sys
sys.path.append("src/gui")
from fsm import *

class MainWidget(QWidget):
    # frameSignal = pyqtSignal(np.ndarray)
    yesSignal = pyqtSignal()
    noSignal = pyqtSignal()
    listenedSignal = pyqtSignal()
    placeSignal = pyqtSignal()
    cancelSignal = pyqtSignal()
    returnSignal = pyqtSignal()
    messageSignal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

        self.signals = [self.placeSignal, 
                        self.messageSignal, 
                        self.returnSignal, 
                        self.cancelSignal,
                        self.listenedSignal, 
                        self.yesSignal, 
                        self.noSignal]
        self.slots = [self.slot1, self.slot2, self.slot3]

        self.label = QLabel()
        self.label.setStyleSheet("color: white; background-color: black")
        self.label.setText(
            "KEYBINDS:\n1-place\n2-message\n3-return\n4-listened\nc-cancel\ny-yes\nn-no"
            )

        self.layout = QGridLayout()
        self.layout.addWidget(self.label, 0, 0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

        self.fsm = FSM(self.signals, self.slots)
        self.fsm.state_machine.start()

    def slot1(self):
        print("slot 1 executed...")

    def slot2(self):
        print("slot 2 executed...")

    def slot3(self):
        print("slot 3 executed...")

    def keyPressEvent(self, event):
        super(MainWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_1:
            self.placeSignal.emit()
        if event.key() == Qt.Key_2:
            self.messageSignal.emit()
        if event.key() == Qt.Key_3:
            self.returnSignal.emit()
        if event.key() == Qt.Key_4:
            self.listenedSignal.emit()
        if event.key() == Qt.Key_C:
            self.cancelSignal.emit()
        if event.key() == Qt.Key_Y:
            self.yesSignal.emit()
        if event.key() == Qt.Key_N:
            self.noSignal.emit()

class UI:
    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.window = QMainWindow()
        self.main_widget = MainWidget()
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    someUI = UI()