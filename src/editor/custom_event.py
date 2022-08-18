import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class CustomEvent(QEvent):
    idType = QEvent.registerEventType()

    def __init__(self, data):
        super(CustomEvent, self).__init__(CustomEvent.idType)
        self.data = data

    def getData(self):
        return self.data