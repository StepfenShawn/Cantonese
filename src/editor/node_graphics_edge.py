import typing
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge,  parent = None) -> None:
        super().__init__(parent)

        self.edge = edge

        # init flags
        self._last_selected_state = False
        self.hovered = False

        # init variables
        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self._color = QColor("#001000")
        self._pen = QPen(self._color)

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemItemIsSelectableIs)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        self.updatePath()
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def updatePath(self):
        pass


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def updatePath(self) -> QPainterPath:
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path

class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def updatePath(self):
        pass