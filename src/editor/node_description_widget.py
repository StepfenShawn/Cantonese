from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AttrNameWidget(QWidget):
    def __init__(self, parent = None, Name : str = 'node name'):
        super(AttrNameWidget, self).__init__(parent)
        self.Name = Name
        self.initUI()

    def initUI(self):
        self.text = QLabel(self.Name)

class AttrDescriptionWidget(QWidget):
    def __init__(self, parent = None) -> None:
        self.initDescriptionMap()
        self.initUI()
        self.descritpion = None

    def initDescriptionMap(self) -> None:
        self.description_map = {
            "入口" : "该程序的入口",
            "输出" : "将参数打印至屏幕上",
            "相加" : "将两个任意类型数字相加, 若都为字符串类型则拼接"
        }

    def initUI(self):
        self.widget = QTextEdit("Description")
        self.widget.setObjectName("DescriptionText")
        self.widget.setFocusPolicy(Qt.NoFocus)
        self.widget.setFontPointSize(14)
        self.widget.setStyleSheet("#DescriptionText{background-color:#8B8B83}")


class w_descriptionWidget(QDockWidget):
    def __init__(self, title_text = '详细面板', parent = None):
        super().__init__(parent)
        self.centreWidget = QWidget()
        self.initLayout()
        self.initBackground()
        self.title_text = title_text
        self._parent = parent

    def initLayout(self):
        """初始化布局"""
        self.h_layout = QVBoxLayout()
        self.h_layout.setSpacing(0)
        self.h_layout.setAlignment(Qt.AlignLeft)
        self.h_layout.setContentsMargins(8,0,0,0)

        self.TextNodeName = AttrNameWidget(self)
        self.W_Description = AttrDescriptionWidget(self)
        self.h_layout.addWidget(self.TextNodeName.text)
        self.h_layout.addWidget(self.W_Description.widget)
        self.centreWidget.setLayout(self.h_layout)
        self.setWidget(self.centreWidget)
        

    def initBackground(self):
        """初始化背景颜色"""
        self.setAutoFillBackground(True) #自动填充背景
        self.setPalette(QPalette(QColor("#4F4F4F"))) #着色区分背景
    
    def click(self,is_click):
        """槽函数-点击"""
        self.click_signal.emit(self,is_click)
        
    def cancelSelected(self):
        """槽函数-取消选中"""
        self.item.is_click = False
        self.item.update()
    
    def mousePressEvent(self, a0: QMouseEvent):
        """重载-鼠标点击"""
        if a0.x()>8 and a0.x()<150:
            self.selected = True#是否选中
            super().mousePressEvent(a0)
        if a0.x()>142 and a0.x()<149:
            self.click_signal_close.emit(self)

    def updateDescriptions(self, name):
        try:
            ctx = self.W_Description.description_map[name]
        except KeyError:
            ctx = "No descriptions"
        self.W_Description.widget.setText(ctx)
        self.TextNodeName.text.setText(name)