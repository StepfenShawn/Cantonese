from node_graphics_node import QDMGraphicsNode
from node_content_widgets import QDMNodeContentWidgets
from node_socket import Socket


class Node():
    def __init__(self, scene, title = "Undefined Node", inputs = [], outputs = []) -> None:
        self.scene = scene
        self.title = title
        self.content = QDMNodeContentWidgets()
        self.grNode = QDMGraphicsNode(self)
        self.scene.grScene.addItem(self.grNode)
        self.scene.addNode(self)


        self.inputs = []
        self.outputs = []
        counter = 0
        for item in inputs:
            socket = Socket(self, index = counter)
            counter += 1
            self.inputs.append(socket)
