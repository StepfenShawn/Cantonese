import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_editor_wnd import NodeEditorWidget
from node_description_bar import DescriptionBar
from custom_event import CustomEvent

class NodeEditorWnd(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.nodeEditorWidgetClass = NodeEditorWidget(self)
        self.initUI()

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        EditMenu = QMenu("&Edit", self)
        menuBar.addMenu(fileMenu)
        menuBar.addMenu(EditMenu)
        self.setMenuBar(menuBar)

    def _createToolBars(self):
        self.dBar = DescriptionBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.dBar.Bar)


    def _updateToolBars(self, node_info = ""):
        self.dBar._nodeName = node_info
        self.dBar.widget.updateNodeName(node_info)
        # self.addToolBar(Qt.LeftToolBarArea, self.dBar.Bar)

    def initUI(self):
        self.setWindowTitle("Cantonese Editor")
        self.setCentralWidget(self.nodeEditorWidgetClass)
        
        self._createToolBars()
        self._createMenuBar()

        self.show()

    def event(self, event: QEvent) -> bool:
        if (event.type() == CustomEvent.idType):
            self._updateToolBars(event.getData().title)
        return super().event(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = NodeEditorWnd()
    sys.exit(app.exec_())