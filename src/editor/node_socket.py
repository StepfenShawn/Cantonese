from node_graphics_socket import QDMGraphicsSocket
from node_graphics_socket import LEFT_TOP
from node_graphics_socket import LEFT_BOTTOM
from node_graphics_socket import RIGHT_TOP
from node_graphics_socket import RIGHT_BOTTOM
from node_graphics_socket import SOCKET_LOGIC_TYPE
from node_graphics_socket import SOCKET_VALUE_TYPE

class Socket():
    def __init__(self, node, index : int = 0, position : int = LEFT_TOP, socket_type : int = SOCKET_LOGIC_TYPE):
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.grSocket = QDMGraphicsSocket(self, position = position, socket_type = socket_type)
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position))

        self.edges = []

    def getSocketPosition(self):
        ret = self.node.getSocketPosition(self.index, self.position)
        return ret

    def delete(self):
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket