from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from node import Node
from node_graphics_socket import SOCKET_LOGIC_TYPE
from node_graphics_socket import SOCKET_VALUE_TYPE


class QSearchNodeBaseSigner(QObject):
    addNode = pyqtSignal(object)
    def __init__(self):
        super(QSearchNodeBaseSigner, self).__init__()
    def addNode_run(self,node_name):
        self.addNode.emit(node_name)

class QDMNodeSearchGraphics(QGraphicsItem):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.initSizes()
        self.initAssets()
        self.initUI()

    def initSizes(self):
        self.width = 350
        self.height = 450

    def initAssets(self):
        self.signer = QSearchNodeBaseSigner()

        self.edge_roundness = 3.0#发亮边缘圆角度数
        self._color = QColor("#363636")
        self._color_roundness = QColor("#FF000000")
        self._pen_roundness = QPen(self._color_roundness)
        self._pen_roundness.setWidthF(2.0)
        #节点背景颜色
        self._brush_background = QBrush(QColor("#1C1C1C"))

    def initUI(self):
        self.push_button_css = '''QPushButton{background:#696969;border-radius:5px;}QPushButton:hover{background:#E8E8E8;}'''
        
        self.push_button = QPushButton("添加程序入口")
        self.push_button.setFixedSize(self.width, 40)
        self.push_button.setStyleSheet(self.push_button_css)
        self.node_widget = QGraphicsProxyWidget(self)
        self.node_widget.setWidget(self.push_button)
        self.push_button.clicked.connect(self.addNode_BeginPlay)

        self.push_button_print = QPushButton("输出")
        self.push_button_print.setFixedSize(self.width, 40)
        self.push_button_print.setStyleSheet(self.push_button_css)
        self.node_widget2 = QGraphicsProxyWidget(self)
        self.node_widget2.setWidget(self.push_button_print)
        self.node_widget2.setY(40)
        self.push_button_print.clicked.connect(self.addNode_PrintString)

        self.push_button_addvar = QPushButton("添加变量")
        self.push_button_addvar.setFixedSize(self.width, 40)
        self.push_button_addvar.setStyleSheet(self.push_button_css)
        self.node_widget3 = QGraphicsProxyWidget(self)
        self.node_widget3.setWidget(self.push_button_addvar)
        self.node_widget3.setY(80)
        self.push_button_addvar.clicked.connect(self.addNode_AddVar)

        self.push_button_addfunc = QPushButton("添加函数")
        self.push_button_addfunc.setFixedSize(self.width, 40)
        self.push_button_addfunc.setStyleSheet(self.push_button_css)
        self.node_widget4 = QGraphicsProxyWidget(self)
        self.node_widget4.setWidget(self.push_button_addfunc)
        self.node_widget4.setY(120)
        self.push_button_addfunc.clicked.connect(self.addNode_AddFunc)



    def addNode_BeginPlay(self):
        self.signer.addNode_run('入口')

    def addNode_PrintString(self):
        self.signer.addNode_run('输出')

    def addNode_AddVar(self):
        self.signer.addNode_run('变量')

    def addNode_AddFunc(self):
        self.signer.addNode_run('函数')

    """
        定义Qt的边框
    """

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    """
        节点主体背景
    """
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, 0, self.width, self.height, self.edge_roundness, self.edge_roundness)
        painter.setPen(self._pen_roundness)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())


class NodeSearch():
    def __init__(self, scene = None) -> None:
        self.scene = scene
        self.initAssets()
        self.create()

    def initAssets(self):
        self.signer = QSearchNodeBaseSigner()

    def create(self):
        self.widget_search = QDMNodeSearchGraphics()
        self.widget_search.signer.addNode.connect(self.addNode)
    
    def remove(self):
        self.scene.grScene.removeItem(self.widget_search)

    def setSearchWidgetLocation(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.widget_search.setPos(x, y)
        self.show()

    def show(self):
        self.scene.grScene.addItem(self.widget_search)

    # TODO
    def addNode(self, name = "默认节点"):
        if name == '入口':
            ret = Node(self.scene, title = name, outputs = [{'type' : SOCKET_LOGIC_TYPE}])
            ret.setPos(self.pos_x, self.pos_y)
            self.remove()
        
        elif name == '输出':
            ret = Node(self.scene, title = name, inputs = [{'type' : SOCKET_LOGIC_TYPE}, {'type' : SOCKET_VALUE_TYPE, 'name' : "参数"}], 
                                                outputs = [{'type' : SOCKET_LOGIC_TYPE}])
            ret.setPos(self.pos_x, self.pos_y)
            self.remove()

        elif name == '变量':
            ret = Node(self.scene, title = name, width = 150, height = 80,outputs = [{'type' : SOCKET_VALUE_TYPE, 'name' : "返回值"}, {'type' : SOCKET_VALUE_TYPE, 'name' : "返回值"}])
            ret.setPos(self.pos_x, self.pos_y)
            self.remove()

        elif name == '函数':
            ret = Node(self.scene, title = name, outputs = [{'type' : SOCKET_LOGIC_TYPE}])
            ret.setPos(self.pos_x, self.pos_y)
            self.remove()

        else:
            return
        
        return ret