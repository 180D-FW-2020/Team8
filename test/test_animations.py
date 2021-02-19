import base_test
from src.gui.animations import *
import numpy as np
import cv2 as cv
import data.resources

DFORMAT = QImage.Format_RGB888 # color space

class TestVideo(QObject):
    image_data = pyqtSignal(np.ndarray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv.VideoCapture(0)
        self.trigger = QBasicTimer()

    def start(self):
        self.trigger.start(0, self)

    def timerEvent(self, event):
        if(event.timerId() != self.trigger.timerId()):
            print("error: timer ID mismatch")
            return
            
        read, frame = self.cap.read()
        if read:
            self.image_data.emit(frame)

class DisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()
        
    def _array2qimage(self, image : np.ndarray):
        h, w, c = image.shape
        bpl = w*3 # bytes per line
        image = QImage(image.data, w, h, bpl, DFORMAT)
        image = image.rgbSwapped()
        return image

    def setImage(self, image):
        self.image = self._array2qimage(image)
        self.setFixedSize(self.image.size())
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawImage(0, 0, self.image)
        self.image = QImage()

class MainWidget(QWidget):
    spawn = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

        # widgets and objects
        self.display = DisplayWidget()
        self.video = TestVideo()
        self.emotebox = EmoteWidget()
        self.frame_timer = QTimer(self)
        
        self.layout = QGridLayout()
        self.setMainLayout()

        # signals and slots
        self.spawn.connect(lambda x: self.emotebox.spawn_emotes(x))
        self.video.image_data.connect(lambda x: self.display.setImage(x))
        self.video.start()

    def setMainLayout(self):
        self.layout.addWidget(self.display, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.emotebox, 0, 0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def keyPressEvent(self, event):
        super(MainWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_Q:
            self.spawn.emit([1,1,1])
        if event.key() == Qt.Key_W:
            self.spawn.emit([2])
        if event.key() == Qt.Key_E:
            self.spawn.emit([3])
        if event.key() == Qt.Key_R:
            self.spawn.emit([4])
        if event.key() == Qt.Key_T:
            self.spawn.emit([5])

class testUI:
    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.window = QMainWindow()
        # self.main_widget = EmoteWidget()
        self.main_widget = MainWidget()
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    test = testUI()