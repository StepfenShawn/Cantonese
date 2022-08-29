import typing

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DescriptionWidgetItem(QWidget):
    click = pyqtSignal(object)
    def __init__(self, title_text, parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.initSize()
        self.initBackground()
        self.initAssets()

        self.is_clicked = False
        self.is_selecte_x = False
        self.title_text = title_text

    def initSize(self):
        """初始化尺寸"""
        self.setMinimumWidth(60)
        self.setMinimumHeight(20)
        self.setMaximumWidth(60)
        self.setGeometry(8,0,60,20)

    def initBackground(self):
        """初始化背景颜色"""
        self.setAutoFillBackground(True)
        self.setPalette(QPalette(QColor("#003c3c3c")))

    def initAssets(self):
        self.font1 = QFont("SimHei", 9)
        self.font2 = QFont("SimHei", 8)
        self.pen_text  = QPen(QColor("#ffffff"))
        self.pen_Text3  = QPen(QColor("#1b1b1b"))
        self.pen_3  = QPen(QColor("#c0b119"))
        self.brush_background = QBrush(QColor("#3c3c3c"))

    def enterEvent(self, a0: QEvent) -> None:
        self.setMouseTracking(True)
        self.brush_background = QBrush(QColor("#363636"))
        self.update()

    def leaveEvent(self, a0: QEvent) -> None:
        self.setMouseTracking(False)
        self.is_selecte_x = False
        self.brush_background = QBrush(QColor("#3c3c3c"))
        self.update()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.brush_background = QBrush(QColor("#3e3e3e"))
        self.update()
        self.is_clicked = not self.is_clicked
        self.click.emit(self.is_clicked)
        super().mousePressEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        x = a0.pos().x()
        if x > 132 and x < 142:
            self.is_selecte_x = True
            self.update()
        else:
            self.is_selecte_x = False
            self.update()
        super().mouseMoveEvent(a0)

    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)

        path_content1 = QPainterPath()
        path_content1.setFillRule(Qt.WindingFill)
        path_content1.addRoundedRect(0, 0, self.width(), self.height(), self.roundnes, self.roundnes)
        path_content1.addRect(0, self.roundnes, self.width(), self.height()-self.roundnes)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush_background)
        painter.drawPath(path_content1.simplified())
        #绘制文字
        painter.setFont(self.font1)
        painter.setPen(self.pen_text)
        painter.drawText(30,15,self.title_text)
        #绘制图片
        painter.drawPixmap(10, 3, 14, 14, self.pix)
        #绘制选中金线
        if self.is_click:
            lg = QLinearGradient(0, 0, self.width(), 0)
            lg.setColorAt(0, QColor("#00c0b119"))
            lg.setColorAt(0.05, QColor("#c0b119"))
            lg.setColorAt(0.95, QColor("#c0b119"))
            lg.setColorAt(1, QColor("#00c0b119"))
            
            brush = QBrush(lg)
            self.pen_3 = QPen(brush,1)
            painter.setPen(self.pen_3)
            painter.drawLine(self.roundnes,0,self.width()-2*self.roundnes,0)
        #绘制叉号
        if self.is_select_x:
            #白色叉号
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor('#b50202')))
            painter.drawEllipse(self.width()-20-0,15-11,12,12)
            painter.setPen(QPen(QColor('#ffffff')))
        else:
            painter.setPen(self.pen_Text3)
            painter.setBrush(Qt.NoBrush)
        painter.setFont(self.font2)
        painter.drawText(self.width()-20,15,'×')
        
        return super().paintEvent(a0)

class w_descriptionWidget(QDockWidget):
    click_signal = pyqtSignal(object,object)
    click_signal_close = pyqtSignal(object)

    def __init__(self, title_text = '详细面板', parent = None):
        super().__init__()
        self.initLayout()
        self.initBackground()
        self.title_text = title_text
        
        self.item = DescriptionWidgetItem(self.title_text)
        self.item.click.connect(self.click)
        self.h_layout.addWidget(self.item)

    def initLayout(self):
        """初始化布局"""
        self.h_layout = QHBoxLayout()
        self.h_layout.setSpacing(0)
        self.h_layout.setAlignment(Qt.AlignLeft)
        self.h_layout.setContentsMargins(8,0,0,0)
        self.setLayout(self.h_layout)#设置布局
    
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