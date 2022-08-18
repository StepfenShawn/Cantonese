import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# Views
from node_graphics_view import QDMGraphicsView

from node import Node
from node_scene import Scene
from node_graphics_socket import SOCKET_VALUE_TYPE
from node_graphics_socket import SOCKET_LOGIC_TYPE

"""
    编辑器主窗口
"""
class NodeEditorWidget(QWidget):
    def __init__(self, MainWnd, parent: typing.Optional['QWidget'] = None):
        super().__init__(parent)
        # 加载节点样式
        self.stylesheet_filename = 'style/node_style.qss'
        self.loadSytlesheet(self.stylesheet_filename)
        self.mainWindow = MainWnd
        self.initUI()


    def initUI(self):
        # 设置窗口大小
        self.setGeometry(200, 200, 800, 900)
 
        # 设置垂直布局
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
 
        # 渲染网格
        self.scene = Scene(self.mainWindow)
        # self.grScene = self.scene.grScene
 
        # 渲染布局
        self.view = QDMGraphicsView(self.scene, self)
        self.layout.addWidget(self.view)
 
        self.addNodes()

    def addNodes(self):
        node1 = Node(self.scene, "相加", inputs=[{'type' : SOCKET_LOGIC_TYPE}, {'type' : SOCKET_VALUE_TYPE}, {'type' : SOCKET_VALUE_TYPE}], outputs=[{'type' : SOCKET_LOGIC_TYPE}])
        node2 = Node(self.scene, "输出", inputs=[{'type' : SOCKET_LOGIC_TYPE}], width = 180, height = 240)
        node2.setPos(-250, -350)
        node3 = Node(self.scene, "入口", inputs=[], outputs=[{'type' : SOCKET_LOGIC_TYPE}])
        node3.setPos(100, 100)
        #node4 = Node(self.scene, "1", inputs = [], outputs=[{'type' : SOCKET_VALUE_TYPE}], height = 70)
        #node5 = Node(self.scene, "2", inputs = [], outputs=[{'type' : SOCKET_VALUE_TYPE}], height = 70)

    def loadSytlesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, 
                                encoding = "utf-8"))