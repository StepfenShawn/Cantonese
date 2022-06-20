from node_graphics_scene import QDMGraphicsScene

class Scene():
    def __init__(self) -> None:
        self.nodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000
        self.initUI()


    def initUI(self) -> None:
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width,
                                self.scene_height)

    def addNode(self, node) -> None:
        self.node.append(node)

    def addEdge(self, edge) -> None:
        self.edges.append(edge)

    def removeNode(self, node) -> None:
        self.nodes.remove(node)

    def removeEdge(self, edge) -> None:
        self.edges.remove(edge)