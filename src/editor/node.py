from node_graphics_node import QDMGraphicsNode
from node_content_widgets import QDMNodeContentWidgets

class Node():
    def __init__(self, scene, title = "Undefined Node") -> None:
        self.scene = scene
        self.title = title
        self.content = QDMNodeContentWidgets()
        self.grNode = QDMGraphicsNode(self)
        self.scene.grScene.addItem(self.grNode)
        self.scene.addNode(self)

        self.inputs = []
        self.outputs = []