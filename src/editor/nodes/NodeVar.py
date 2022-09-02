from node import *
from node_socket import *
from node_graphics_socket import *
from res.setting import LanguageSetter

class _NodeVar(Node):
    def __init__(self, scene) -> None:
        self.scene = scene
        self.title = LanguageSetter("cn").read()['NodeVarName']
        self.outputs = [{'type' : SOCKET_VALUE_TYPE_STRING, 'name' : "返回值"}]
        self.node_type = NODE_VARAIBLE_TYPE
        self.node = Node(self.scene, self.title, outputs = self.outputs, node_type = self.node_type)
        print(self._compile())

    def _compile(self):
        return self.node.outputs[0].getData()