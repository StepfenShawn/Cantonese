import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_editor_wnd import NodeEditorWidget
# from node_description_bar import DescriptionBar
from custom_event import CustomEvent

from node_eval import Eval
from node_description_widget import w_descriptionWidget

class NodeEditorWnd(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.nodeEditorWidgetClass = NodeEditorWidget(self)
        self.initUI()

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        menuBar.setObjectName("Menu")
        menuBar.setStyleSheet("#Menu{background-color:#F0FFFF}")

        fileMenu = QMenu("&File", self)
        EditMenu = QMenu("&Edit", self)
        runMenu = QMenu("&Run", self)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)

        runMenu.addAction(self.compileAction)

        menuBar.addMenu(EditMenu)
        menuBar.addMenu(runMenu)

        self.setMenuBar(menuBar)

    def _createActions(self):
        self.newAction = QAction("&new", self)
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save as", self)

        self.compileAction = QAction("&Compile", self)
        self.compileAction.triggered.connect(self.compile)

    def _createViewDescription(self):
        self.view_description = w_descriptionWidget(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.view_description)

    def _updateToolBars(self, node_info = ""):
        self.dBar._nodeName = node_info
        self.dBar.widget.updateNodeName(node_info)

    def initUI(self):
        self.setWindowTitle("Cantonese Editor")
        self.setCentralWidget(self.nodeEditorWidgetClass)
        
        self._createViewDescription()
        self._createActions()
        self._createMenuBar()

        self.show()

    def event(self, event: QEvent) -> bool:
        if (event.type() == CustomEvent.idType):
            # self._updateToolBars(event.getData().title)
            pass
        return super().event(event)

    def compile(self):
        print("----------------")
        for node in self.nodeEditorWidgetClass.scene.nodes:
            print(Eval(node).trans())
        print("----------------")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = NodeEditorWnd()
    sys.exit(app.exec_())