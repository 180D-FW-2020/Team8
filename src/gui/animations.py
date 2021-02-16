from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
sys.path.append('data')
import resources
import random

sys.path.append('data')

import resources

WIDTH = 640
HEIGHT = 480
XCENTER = WIDTH//2
YCENTER = HEIGHT//2

EMOTEIDS = {
   1 : ":/emotes/angry",
   2 : ":/emotes/cringe",
   3 : ":/emotes/cry",
   4 : ":/emotes/doubt",
   5 : ":/emotes/LOL",
   6 : ":/emotes/welp",
   7 : ":/emotes/frown",
   8 : ":/emotes/grin",
   9 : ":/emotes/love",
   10 : ":/emotes/ofcourse",
   11 : ":/emotes/shock",
   12 : ":/emotes/simp",
   13 : ":/emotes/smile",
   14 : ":/emotes/hmmm",
   15 : ":/emotes/tongue",
   16 : ":/emotes/wink"
}

class EmoteWidget(QWidget):
    test = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.resize(WIDTH,HEIGHT)

        self.base = QLabel(self)
        self.base_pixmap = QPixmap(WIDTH, HEIGHT) # blank display
        self.base_pixmap.fill(Qt.transparent)
        self.base.setPixmap(self.base_pixmap)

        self.layout = QGridLayout()
        self.set_layout()

        self.animations_group = QParallelAnimationGroup()

        ## signals and slots
        # self.test.connect(self.create_animation)
        self.test.connect(lambda x: self.spawn_emotes(x))
        self.animations_group.finished.connect(self.clearAnimations)

    def create_animation(self, emoteID):
        emotebox = QLabel(self)
        emote_pixmap = QPixmap(EMOTEIDS[emoteID])

        emotebox.resize(200,200)
        emotebox.setPixmap(
            emote_pixmap.scaled(
                100,100,Qt.KeepAspectRatio,Qt.SmoothTransformation
                )
            )

        effect = QGraphicsOpacityEffect(emotebox)
        emotebox.setGraphicsEffect(effect)
        anim = QPropertyAnimation(emotebox, b"pos")
        anim_3 = QPropertyAnimation(effect, b"opacity")
        anim_2 = QPropertyAnimation(effect, b"opacity")
        anim_initial = QSequentialAnimationGroup()
        anim_final = QParallelAnimationGroup()

        easing_curve = QEasingCurve(random.randint(0,40))
        start_pos = (random.randint(WIDTH//4,3*WIDTH//4), 
                     random.randint(HEIGHT//4,3*HEIGHT//4))
        end_pos = (random.randint(0,WIDTH), 
                   random.randint(0,HEIGHT))

        anim.setStartValue(QPoint(start_pos[0],start_pos[1]))
        anim.setEndValue(QPoint(end_pos[0], end_pos[1]))
        anim.setEasingCurve(easing_curve)
        anim.setDuration(3000)

        anim_2.setStartValue(0)
        anim_2.setEndValue(1)
        anim_2.setDuration(1500)

        anim_3.setStartValue(1)
        anim_3.setEndValue(0)
        anim_3.setDuration(1500)

        anim_initial.addAnimation(anim_2)
        anim_initial.addAnimation(anim_3)
        anim_final.addAnimation(anim_initial)
        anim_final.addAnimation(anim)
        emotebox.setHidden(False)
        
        self.addToAnimationsQueue(anim_final)

    def spawn_emotes(self, listIDs):
        for emoteID in listIDs:
            self.create_animation(emoteID)

    def set_layout(self):
        self.setLayout(self.layout)
        self.layout.addWidget(self.base,0,0,alignment=Qt.AlignCenter)

    def addToAnimationsQueue(self, animation):
        self.animations_group.addAnimation(animation)
        self.animations_group.start()
        
    def clearAnimations(self):
        self.animations_group.clear()
        for widget in range(1,self.layout.count()):
            self.deleteWidget(widget)

    def deleteWidget(self, widget):
        self.layout.removeWidget(widget)
        widget.deleteLater()
        widget = None