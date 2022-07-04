from PyQt5.QtWidgets import *

"""
    节点内容类
"""
class QDMNodeContentWidgets(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # 垂直布局
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # self.wdg_label = QLabel("Comment")
        # self.layout.addWidget(self.wdg_label)
        # text = QTextEdit("注释")
        # self.layout.addWidget(text)

    