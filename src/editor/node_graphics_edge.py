import typing
import math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from node_graphics_socket import LEFT_BOTTOM
from node_graphics_socket import LEFT_TOP
from node_graphics_socket import RIGHT_BOTTOM
from node_graphics_socket import RIGHT_TOP

EDGE_TYPE_DIRECT = 1 # 直线
EDGE_TYPE_BEZIER = 2 # 曲线

EDGE_CP_ROUNDNESS = 100

class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge,  parent = None, type : int = EDGE_TYPE_BEZIER) -> None:
        super().__init__(parent)

        self.edge = edge
        # 线条的宽度
        self.width = 3.0
        # init flags
        self._last_selected_state = False
        self.hovered = False
        self._type = type

        # init variables
        self.posSource = [0, 0] # 线条起始位置
        self.posDestination = [0, 0] # 线条终止位置

        self._color = QColor("#F8F8FF")
        self._pen = QPen(self._color)
        self._pen.setWidthF(self.width)

        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashDotLine)
        self._pen_dragging.setWidthF(self.width)

        # 设置线条可选
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.posSource = [x, y]

    def set_dst(self, x, y):
        self.posDestination = [x, y]

    # Override
    def shape(self) -> QPainterPath:
        return self.updatePath()

    # Override
    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()

    # Override
    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        self.setPath(self.updatePath())
        path = self.path()
        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
            painter.drawPath(path)
        else:
            painter.setPen(self._pen)
            painter.drawPath(path)

    def updatePath(self):
        if self._type == EDGE_TYPE_DIRECT:
            path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))  # 起点
            path.lineTo(self.posDestination[0], self.posDestination[1])  # 终点
            return path
        elif self._type == EDGE_TYPE_BEZIER:
            s = self.posSource
            d = self.posDestination
            dist = (d[0] - s[0]) * 0.5

            cpx_s = +dist
            cpx_d = -dist
            cpy_s = 0
            cpy_d = 0

            if self.edge.start_socket is not None:
                sspos = self.edge.start_socket.position
                if (s[0] > d[0] and sspos in (RIGHT_TOP, RIGHT_BOTTOM)) or (
                    s[0] < d[0] and sspos in (LEFT_TOP, LEFT_BOTTOM)):
                    cpx_d *= 1
                    cpx_s *= -1

                    
                    cpy_d = (
                                (s[1] - d[1]) / math.fabs(
                            (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                        )
                        ) * EDGE_CP_ROUNDNESS
                    cpy_s = (
                                (d[1] - s[1]) / math.fabs(
                            (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                        )
                        ) * EDGE_CP_ROUNDNESS

            path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
            path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0],
                        self.posDestination[1])
            return path
