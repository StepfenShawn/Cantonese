from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from custom_event import CustomEvent

"""
    节点图像类
"""
class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node, scene, parent = None, width = 180, height = 100):
        super().__init__(parent)
        self._scene = scene
        self.node = node
        self.content = self.node.content
 
        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", 10)

        self.width = width
        self.height = height
        self.edge_size = 10.0
        self.title_height = 24.0
        self._padding = 4.0

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))
 
        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))
 
        # init title
        self.initTitle()
        self.title = self.node.title

        # init sockets
        self.initSocket()


        # init content
        self.initContent()


        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
    
    # 初始化标题
    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(
                self.width
                - 2 * self._padding
            )
    
    @property
    def title(self): 
        return self._title
        
    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def setTitle(self, t):
        self.title = t


    # 初始化套接字
    def initSocket(self):
        pass

    # 初始化内容
    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size,
            self.title_height + self.edge_size,
            self.width - 6 * self.edge_size,
            self.height - 3 * self.edge_size - self.title_height)
        self.grContent.setWidget(self.content)

    def boundingRect(self):
        return QRectF(
                0,
                0,
                self.width,
                self.height
            ).normalized()
    
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())
    
    
        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())
    
    
        # outline , 边框颜色及被选中颜色
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())


    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)
        if self.isSelected():
            for gr_edge in self._scene.edges:
                gr_edge.edge.update_positions()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        postEvent = CustomEvent(self.node)
        QCoreApplication.postEvent(self._scene.MainWindow, postEvent)
        return super().mousePressEvent(event)