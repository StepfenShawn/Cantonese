from node_graphics_node import QDMGraphicsNode
from node_content_widgets import QDMNodeContentWidgets
from node_socket import Socket
from node_socket import LEFT_TOP
from node_socket import LEFT_BOTTOM
from node_socket import RIGHT_TOP
from node_socket import RIGHT_BOTTOM
from node_socket import SOCKET_LOGIC_TYPE
from node_socket import SOCKET_VALUE_TYPE

class Node():
    def __init__(self, scene, title = "Undefined Node", inputs = [], outputs = [], width = 180, height = 100) -> None:
        self.scene = scene
        self.title = title
        self.content = QDMNodeContentWidgets()
        # TODO: define different node type's height and width
        self.grNode = QDMGraphicsNode(self, scene, width = width, height = height)
        self.scene.grScene.addItem(self.grNode)
        self.scene.addNode(self)


        self.socket_spacing = 22

        self.inputs = []
        self.outputs = []
        counter = 0
        for item in inputs:
            try:
                socket_type = item['type']
            except KeyError:
                # 设置为默认的类型
                pass
            socket = Socket(self, index = counter, position = LEFT_TOP, socket_type = socket_type)
            counter += 1
            self.inputs.append(socket)
        counter = 0
        for item in outputs:
            try:
                socket_type = item['type']
            except KeyError:
                # 设置为默认的类型
                pass
            socket = Socket(self, index = counter, position = RIGHT_TOP, socket_type = socket_type)
            counter += 1
            self.outputs.append(socket)

    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPosition(self, index, position):
        if position in (LEFT_TOP, LEFT_BOTTOM):
            x = 0
        else:
            x = self.grNode.width - self.socket_spacing
        
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.edge_size - \
                self.grNode._padding - index * self.socket_spacing
        else:
            # start form top
            y = self.grNode.title_height + self.grNode._padding \
                + self.grNode.edge_size + index * self.socket_spacing
        return x, y

    def remove(self):
        for socket in (self.inputs + self.outputs):
            if socket.isConnected:
                socket.edge.remove()
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None