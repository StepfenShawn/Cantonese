from node_graphics_socket import QDMGraphicsSocket
from node_graphics_socket import LEFT_TOP
from node_graphics_socket import LEFT_BOTTOM
from node_graphics_socket import RIGHT_TOP
from node_graphics_socket import RIGHT_BOTTOM

class Socket():
    def __init__(self, node, index : int = 0, position : int = LEFT_TOP, socket_type : int = 1):
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.grSocket = QDMGraphicsSocket(self, position = position)
        self.grSocket.setPos(*self.node.getSocketPosition(index, position))

    def delete(self):
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket