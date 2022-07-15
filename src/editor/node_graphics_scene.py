import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

"""
    网格布局
"""
class QDMGraphicsScene(QGraphicsScene):
    itemSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()
    def __init__(self, scene, parent = None):
        super().__init__(parent)

        self.scene = scene

        # settings
        self.gridSize = 20
        self.gridSquares = 5
 
        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")
 
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)
 
        # self.scene_width, self.scene_height = 64000, 64000
 
        self.setBackgroundBrush(self._color_background)

    def setGrScene(self, width, height):
        self.setSceneRect(-width//2, -height//2, width, height)


    # 渲染背景
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)

        # 创建网格
        left   = int(math.floor(rect.left()))   # -400
        right  = int(math.ceil(rect.right()))   # 400
        top    = int(math.floor(rect.top()))    # -300
        bottom = int(math.ceil(rect.bottom()))  #  300
 
        first_left = left - (left % self.gridSize)    #-400
        first_top  = top - (top % self.gridSize)      #-300

        # 计算所有网格
        # 不是100的整数倍的时候加入亮的, 反之加入暗的
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize*self.gridSquares) != 0): 
                lines_light.append(QLine(x, top, x, bottom))
            else: 
                lines_dark.append(QLine(x, top, x, bottom))
 
        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize*self.gridSquares) != 0): 
                lines_light.append(QLine(left, y, right, y))
            else: 
                lines_dark.append(QLine(left, y, right, y))
 
 
        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)
 
        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)