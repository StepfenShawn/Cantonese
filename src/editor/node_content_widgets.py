from tkinter import Widget
from PyQt5.QtWidgets import *

class QDMNodeContentWidgets(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Comment")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QTextEdit("注释"))

    