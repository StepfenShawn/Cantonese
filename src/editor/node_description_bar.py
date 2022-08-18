import typing

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DescriptionBarWidget(QWidget):
    def __init__(self, Name : str, parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.Name = Name
        self.initDescriptionMap()
        self.initUI()
        self.initAssets()

    def initDescriptionMap(self) -> None:
        self.description_map = {
            "入口" : "该程序的入口",
            "输出" : "将参数打印至屏幕上",
            "相加" : "将两个任意类型数字相加, 若都为字符串类型则拼接"
        }

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        self.nodeName = QLabel(self.Name)
        self.text = QTextEdit("Description")

        self.nodeName.setObjectName("nodeName")

        self.text.setObjectName("Text")
        self.text.setFocusPolicy(Qt.NoFocus)
        self.text.setFontPointSize(14)
        self.text.setStyleSheet("#Text{background-color:#8B8B83}")


        self.layout.addWidget(self.nodeName)
        # TODO: self.layout.addWidget(QLabel("ID"))
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)

    def updateNodeName(self, n):
        self.Name = n
        self.nodeName.setText(n)
        self.updateDescription()
        self.update()

    # TODO
    def updateDescription(self):
        try:
            ctx = self.description_map[self.Name]
        except KeyError:
            # ctx = self.description_map[self.nodeType]
            ctx = "No descriptions"
        self.text.setText(ctx)


    def initAssets(self):
        pass

# TODO
class DescriptionBar():
    def __init__(self, mainWnd, nodeName = ""):
        self.Bar = QToolBar("Edit", mainWnd)
        self._nodeName = nodeName
        self.create()

    def create(self):
        self.qss = "#DescriptionBar{background-color:#363636}"
        self.Bar.setObjectName("DescriptionBar")
        self.Bar.setStyleSheet(self.qss)
        self.Bar.setFixedWidth(400)
        self.Bar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)

        self.widget = DescriptionBarWidget(self._nodeName)
        self.Bar.addWidget(self.widget)