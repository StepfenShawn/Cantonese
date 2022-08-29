from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_edge import Edge
from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node import Node
from node_search import NodeSearch
from node_graphics_socket import SocketProxyWidget


MODE_EDITING = 1
MODE_NODE_SEARCHING = 2
MODE_RUNNING = 3

class QDMGraphicsView(QGraphicsView):
    def __init__(self, Scene, parent = None):
        super().__init__(parent)
        self.Scene = Scene
        self.grScene = self.Scene.grScene
        self.initUI()

        self.zoomInFactor = 1.25
        self.zoomClamp = False
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        self.edge_enable = False
        self.drag_edge = None

        self.mode = MODE_RUNNING

        self.bp_search = NodeSearch(self.Scene)
        


    def initUI(self):
        self.setScene(self.grScene)
        # 图像品质
        self.setRenderHints(QPainter.Antialiasing | 
                            QPainter.HighQualityAntialiasing | 
                            QPainter.TextAntialiasing | 
                            QPainter.SmoothPixmapTransform)
        # 全部刷新
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)        

        self.setDragMode(self.RubberBandDrag)
        self.setAcceptDrops(True)
    
    # override
    def keyPressEvent(self, event) -> None:
        # TODO: delete the node
        if event.key() == Qt.Key_D:
            self.Key_D_Press(event)
        elif event.key() == Qt.Key_Delete:
            self.deleteSelected()
        return super().keyPressEvent(event)


    def deleteSelected(self) -> None:
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
                
            elif hasattr(item, 'node'):
                item.node.remove()

    # 鼠标事件处理
    def mousePressEvent(self, event):
        self.setStartPos(event.pos())
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.setDragMode(self.RubberBandDrag)
            self.setAcceptDrops(True)
            if self.mode == MODE_NODE_SEARCHING:
                x, y = self.mapToScene(event.pos()).x(), self.mapToScene(event.pos()).y()
                if ((x < self.bp_search.pos_x or x > self.bp_search.pos_x + self.bp_search.widget_search.width) \
                    and (y > self.bp_search.pos_y or y < self.bp_search.pos_y + self.bp_search.widget_search.height)):
                    self.mode = MODE_RUNNING
                    self.bp_search.remove()
            item = self.get_item_at_click(event)
            if isinstance(item, QDMGraphicsSocket):
                if item.hoverEnter:
                    self.edge_enable = True
                    self.edge_drag_start(item)
            elif isinstance(item, SocketProxyWidget):
                if item.parent.hoverEnter:
                    self.edge_enable = True
                    self.edge_drag_start(item.parent)
            else:
                self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    # Override
    def mouseMoveEvent(self, event):
    	# 实时更新线条
        pos = event.pos()
        if self.drag_edge is not None and self.edge_enable:
            sc_pos = self.mapToScene(pos)
            self.drag_edge.grEdge.set_dst(sc_pos.x(), sc_pos.y())
            self.drag_edge.grEdge.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            if self.edge_enable:
                self.edge_enable = False
                item = self.get_item_at_click(event)
                if (isinstance(item, QDMGraphicsSocket)) and item is not self.drag_start_socket:
                    self.edge_drag_end(item)
                elif (isinstance(item, SocketProxyWidget)) and (isinstance(item.parent, QDMGraphicsSocket)) and item.parent is not self.drag_start_socket:
                    self.edge_drag_end(item.parent)
                else:
                    self.mode = MODE_NODE_SEARCHING
                    self.bp_search.setSearchWidgetLocation(self.mapToScene(event.pos()).x(), 
                                                           self.mapToScene(event.pos()).y())
                    self.drag_edge.remove()
                    self.drag_edge = None
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            sc_pos = self.mapToScene(event.pos())
            if sc_pos == self.mapToScene(self.getStartPos()):
                self.mode = MODE_NODE_SEARCHING
                self.bp_search.setSearchWidgetLocation(sc_pos.x(),sc_pos.y())
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)
 
    # 放大功能 - 按下 
    def middleMouseButtonPress(self, event):
        super().mousePressEvent(event)
 
 
    #  缩小功能 - 松开 
    def middleMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)
 
 
    def leftMouseButtonPress(self, event):
        return super().mousePressEvent(event)
 
    def leftMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
 
    def rightMouseButtonPress(self, event):
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        return super().mousePressEvent(fakeEvent)

    def Key_D_Press(self, event):
        if self.mode == MODE_NODE_SEARCHING:
            self.bp_search.remove()
            self.mode == MODE_RUNNING
        return super().keyPressEvent(event)
 
    def rightMouseButtonRelease(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        super().mouseReleaseEvent(event)
        self.setDragMode(self.NoDrag)

    def get_item_at_click(self, event):
        pos = event.pos()
        item = self.itemAt(pos)
        return item
 
    def edge_drag_start(self, socket):
        self.drag_start_socket = socket
        self.drag_edge = Edge(self.Scene, self.drag_start_socket, None)
    
    def edge_drag_end(self, socket):
        new_edge = Edge(self.Scene, self.drag_start_socket, socket)  # 拖拽结束
        self.drag_edge.remove()  # 删除拖拽时画的线
        self.drag_edge = None
        new_edge.store()  # 保存最终产生的连接线
 
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


    """
        TODO:
        添加一个节点
    """
    def addNodes(self, name = "默认节点"):
        return Node(self.scene, title=name)

    def getStartPos(self):
        return self.start_pos

    def setStartPos(self, pos):
        self.start_pos = pos