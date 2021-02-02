from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

WIDTH = 640
HEIGHT = 480
XCENTER = WIDTH//2
YCENTER = HEIGHT//2

class EmoteWidget(QWidget):
    test = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(WIDTH,HEIGHT)

        self.base = QLabel(self)
        self.emotebox = QLabel(self)
        self.base_pixmap = QPixmap(WIDTH, HEIGHT) # blank display
        self.base_pixmap.fill(Qt.transparent)
        self.emote_pixmap = QPixmap(":/emotes/notimpressed.png")
        self.base.setPixmap(self.base_pixmap)
        self.emotebox.setPixmap(self.emote_pixmap.scaled(WIDTH//16,
                                                         WIDTH//16,
                                                         Qt.KeepAspectRatio,
                                                         Qt.SmoothTransformation))
        self.emotebox.setScaledContents(True)
        self.emotebox.setHidden(True)

        effect = QGraphicsOpacityEffect(self.emotebox)
        self.emotebox.setGraphicsEffect(effect)
        self.anim = QPropertyAnimation(self.emotebox, b"pos")
        self.anim_2 = QPropertyAnimation(effect, b"opacity")
        self.anim_3 = QPropertyAnimation(self.emotebox, b"pos")
        self.anim_4 = QPropertyAnimation(effect, b"opacity")
        self.anim_initial = QParallelAnimationGroup()
        self.anim_final = QParallelAnimationGroup()
        self.anim_full = QSequentialAnimationGroup()

        # self.create_animation()

        ## signals and slots
        self.test.connect(self.create_animation)

        self.layout = QGridLayout()
        self.set_layout()

    def create_animation(self):
        self.anim.setStartValue(QPoint(0,YCENTER))
        self.anim.setEndValue(QPoint(XCENTER, YCENTER))
        self.anim.setDuration(1500)

        self.anim_2.setStartValue(0)
        self.anim_2.setEndValue(1)
        self.anim_2.setDuration(1500)

        self.anim_3.setStartValue(QPoint(XCENTER, YCENTER))
        self.anim_3.setEndValue(QPoint(WIDTH, YCENTER))
        self.anim_3.setDuration(1500)

        self.anim_4.setStartValue(1)
        self.anim_4.setEndValue(0)
        self.anim_4.setDuration(1500)

        self.anim_initial.addAnimation(self.anim)
        self.anim_initial.addAnimation(self.anim_2)
        self.anim_final.addAnimation(self.anim_3)
        self.anim_final.addAnimation(self.anim_4)
        self.anim_full.addAnimation(self.anim_initial)
        self.anim_full.addAnimation(self.anim_final)
        self.emotebox.setHidden(False)
        self.anim_full.start()

    def create_pen(self):
        pen = QPen()
        pen.setWidth(5)
        pen.setColor(QColor('red'))
        return pen

    def set_layout(self):
        self.layout.addWidget(self.base,0,0,alignment=Qt.AlignCenter)
        self.layout.addWidget(self.emotebox,0,0,alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
