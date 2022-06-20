from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QDMGraphicsView(QGraphicsView):
    def __init__(self, grScene, parent = None):
        super().__init__(parent)
        self.grScene = grScene
        self.initUI()
        self.setScene(self.grScene)

        self.zoomInFactor = 1.25
        self.zoomClamp = False
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]


    def initUI(self):
        # 图像品质
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        # 全部刷新
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)        

    
    # 鼠标事件处理
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.rightMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)
 
    # 放大功能 - 按下 
    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, 
                            event.localPos(), event.screenPos(),
                             Qt.MiddleButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        # 设置画布拖拽
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), 
                            event.screenPos(),
                            Qt.MiddleButton, event.buttons() | Qt.LeftButton, 
                            event.modifiers())
        super().mousePressEvent(fakeEvent)
 
 
    #  缩小功能 - 松开 
    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), 
                              event.screenPos(),
                              Qt.LeftButton, event.buttons() & ~Qt.LeftButton, 
                              event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        # 取消拖拽
        self.setDragMode(QGraphicsView.NoDrag)
 
 
    def leftMouseButtonPress(self, event):
        return super().mousePressEvent(event)
 
    def leftMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
 
    def rightMouseButtonPress(self, event):
        return super().mousePressEvent(event)
 
    def rightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
 
 
    # 滚轮缩放的实现
    def wheelEvent(self, event):
        # calculate our zoom Factor
      
        zoomOutFactor = 1 / self.zoomInFactor
 
        # calculate zoom
        # 放大触发
        if event.angleDelta().y() > 0:
            #放大比例 1.25
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        # 缩小触发
        else:
            # 缩小的比例 0.8
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep
        # self.zoomRange[0] = 0 , self.zoomRange[1] =10
        # 限制缩放
        # 取消缩放 
        clamped = False
        if self.zoom < self.zoomRange[0]: 
                  self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: 
                  self.zoom, clamped = self.zoomRange[1], True
 
        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)