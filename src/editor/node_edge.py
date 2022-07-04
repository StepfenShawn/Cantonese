from node_graphics_edge import QDMGraphicsEdge
from node_graphics_edge import QDMGraphicsEdgeDirect
from node_graphics_edge import QDMGraphicsEdgeBezier

EDGE_TYPE_DIRECT = 1 # 直线
EDGE_TYPE_BEZIER = 2 # 曲线

class Edge():
    def __init__(self, scene, start_socket = None, end_socket = None, edge_type : int = EDGE_TYPE_DIRECT) -> None:
        self.scene = scene

        # default init
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type
        self.grEdge = QDMGraphicsEdge()
        # self.scene.addEdge(self)
        self.scene.grScene.addItem(self.grEdge)

        @property
        def start_socket(self):
            return self._start_coket

        @start_socket.setter
        def start_socket(self, value):
            # 如果已经被连接
            if self._start_socket is not None:
                self._start_socket.removeEdge(self)

            self._start_socket = value
            if self.start_scoket is not None:
                self.start_socket.addEdge(self)

        @property
        def end_socket(self):
            return self._end_socket

        @end_socket.setter
        def end_socket(self, value):
            # 如果已经被连接
            if self._end_socket is not None:
                self._end_socket.removeEdge(self)

            self._end_socket = value
            if self.end_socket is not None:
                self.end_socket.addEdge(self)

        @property
        def edge_type(self):
            return self._edge_type

        @edge_type.setter
        def edge_type(self, value):
            if hasattr(self, 'grEdge') and self.grEdge is not None:
                self.scene.grScene.removeItem(self.grEdge)

            self._edge_type = value

            if self.edge_type == EDGE_TYPE_DIRECT:
                self.grEdge = QDMGraphicsEdgeDirect(self)

            elif self.edge_type == EDGE_TYPE_BEZIER:
                self.grEdge = QDMGraphicsEdgeBezier(self)

            else:
                 self.grEdge = QDMGraphicsEdgeBezier(self)

            self.scene.grScene.addItem(self.grEdge)
            if self.start_socket is not None:
                self.updatePositions()