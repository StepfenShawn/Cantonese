import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_editor_wnd import NodeEditorWidget
from node_description_bar import DescriptionBar

class NodeEditorWnd(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.nodeEditorWidgetClass = NodeEditorWidget()
        self.initUI()

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        EditMenu = QMenu("&Edit", self)
        menuBar.addMenu(fileMenu)
        menuBar.addMenu(EditMenu)
        self.setMenuBar(menuBar)

    def _createToolBars(self):
        self.addToolBar(Qt.LeftToolBarArea, DescriptionBar(self).Bar)


    def initUI(self):
        self.setWindowTitle("Cantonese Editor")
        self.setCentralWidget(self.nodeEditorWidgetClass)
        
        self._createToolBars()
        self._createMenuBar()

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = NodeEditorWnd()
    sys.exit(app.exec_())