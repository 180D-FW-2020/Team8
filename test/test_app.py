from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

sys.path.append("src/gui")

import app

# @desc
# initializes all UI widgets
class UI:
    def __init__(self):
        self.qapp = QApplication(sys.argv)
        screen = self.qapp.primaryScreen()
        size = screen.size()
        sizes = (size.width(),size.height())
        self.window = QMainWindow()
        self.main_widget = app.MainWidget(sizes)
        self.window.setCentralWidget(self.main_widget)
        self.window.show()
        sys.exit(self.qapp.exec_())

if __name__ == '__main__':
    someUI = UI()