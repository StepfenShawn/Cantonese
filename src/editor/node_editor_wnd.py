import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_graphics_view import QDMGraphicsView
from node import Node
from node_scene import Scene

class NodeEditorWnd(QWidget):
    def __init__(self, parent: typing.Optional['QWidget'] = None):
        super().__init__(parent)
        self.stylesheet_filename = 'style/node_style.qss'
        self.loadSytlesheet(self.stylesheet_filename)
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 800, 600)
 
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
 
        # 渲染网格
        self.scene = Scene()
        self.grScene = self.scene.grScene

        node = Node(self.scene, "Node1")
 
        # 渲染布局
        self.view = QDMGraphicsView(self.grScene, self)
        self.layout.addWidget(self.view)
 
        self.setWindowTitle("Cantonese Editor")
        self.show()

    def loadSytlesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, 
                                encoding="utf-8"))