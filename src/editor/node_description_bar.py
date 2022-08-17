from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# TODO
class DescriptionBar():
    def __init__(self, mainWnd):
        self.Bar = QToolBar("Edit", mainWnd)
        self.create()

    def create(self):
        self.qss = "#DescriptionBar{background-color:#363636}"
        self.Bar.setObjectName("DescriptionBar")
        self.Bar.setStyleSheet(self.qss)
        self.Bar.setFixedWidth(200)
        self.Bar.setMovable(True)
        self.Bar.setAcceptDrops(True)