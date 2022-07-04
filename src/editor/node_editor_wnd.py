import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_graphics_view import QDMGraphicsView
from node import Node
from node_scene import Scene
from node_socket import Socket

"""
    编辑器主窗口
"""
class NodeEditorWnd(QWidget):
    def __init__(self, parent: typing.Optional['QWidget'] = None):
        super().__init__(parent)
        # 加载节点样式
        self.stylesheet_filename = 'style/node_style.qss'
        self.loadSytlesheet(self.stylesheet_filename)
        self.initUI()

    def initUI(self):
        # 设置窗口大小
        self.setGeometry(200, 200, 800, 600)
 
        # 设置垂直布局
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
 
        # 渲染网格
        self.scene = Scene()
        self.grScene = self.scene.grScene
 
        # 渲染布局
        self.view = QDMGraphicsView(self.grScene, self)
        self.layout.addWidget(self.view)
 
        self.addNodes()

        self.setWindowTitle("Cantonese Editor")
        self.show()

    def addNodes(self):
        node1 = Node(self.scene, "Add", inputs=[1,2], outputs=[1])
        node2 = Node(self.scene, "Print", inputs=[1], width=180, height=240)
        node2.setPos(-250, -350)

    def loadSytlesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, 
                                encoding="utf-8"))