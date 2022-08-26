from node_graphics_scene import QDMGraphicsScene

"""
    场景类, 管理所有节点
"""

class Scene():
    def __init__(self, MainWindow) -> None:
        self.nodes = []
        self.selectedNodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000
        self.initUI()
        
        self.data = []

        self.MainWindow = MainWindow


    def initUI(self) -> None:
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width,
                                self.scene_height)

    def addNode(self, node) -> None:
        self.nodes.append(node)

    def addSelectedNodes(self, node) -> None:
        self.selectedNodes.append(node)

    def addEdge(self, edge) -> None:
        self.edges.append(edge)

    def removeNode(self, node) -> None:
        self.nodes.remove(node)

    def removeEdge(self, edge) -> None:
        self.edges.remove(edge)