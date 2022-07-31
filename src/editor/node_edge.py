from node_graphics_edge import QDMGraphicsEdge
from node_graphics_edge import EDGE_TYPE_DIRECT
from node_graphics_edge import EDGE_TYPE_BEZIER
from node_graphics_socket import QDMGraphicsSocket

class Edge():
    def __init__(self, scene, start_socket : QDMGraphicsSocket = None, 
                end_socket : QDMGraphicsSocket = None, edge_type : int = EDGE_TYPE_BEZIER) -> None:
        self.scene = scene

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type
        self.grEdge = QDMGraphicsEdge(self, type = edge_type)
        self.scene.addEdge(self.grEdge)
        self.scene.grScene.addItem(self.grEdge)

        if self.start_socket is not None:
            self.update_positions()


    def store(self):
        self.scene.addEdge(self.grEdge)
        self.scene.grScene.addItem(self.grEdge)

    def update_positions(self):
        source_pos = [None, None]
        if self.start_socket is not None:
            source_pos[0], source_pos[1] = self.start_socket.socket.getSocketPosition()
            source_pos[0] += self.start_socket.socket.node.grNode.pos().x()
            source_pos[1] += self.start_socket.socket.node.grNode.pos().y()
            self.grEdge.set_src(source_pos[0], source_pos[1])
            if self.end_socket is not None:
                end_pos = [None, None]
                end_pos[0], end_pos[1] = self.end_socket.socket.getSocketPosition()
                end_pos[0] += self.end_socket.socket.node.grNode.pos().x()
                end_pos[1] += self.end_socket.socket.node.grNode.pos().y()
                self.grEdge.set_dst(end_pos[0], end_pos[1])
            else:
                self.grEdge.set_dst(source_pos[0], source_pos[1])
        
            self.grEdge.update()

    def remove_from_current_items(self):
        self.end_socket = None
        self.start_socket = None

    def remove(self):
        self.remove_from_current_items()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        try:
            self.scene.removeEdge(self.grEdge)
        except ValueError:
            pass