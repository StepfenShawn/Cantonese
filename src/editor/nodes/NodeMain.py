from node import Node
from node_socket import SOCKET_LOGIC_TYPE
from res.setting import LanguageSetter

class _NodeMain(Node):
    def __init__(self, scene):
        self.scene = scene
        self.title = LanguageSetter("cn").read()['NodeMainName']
        self.outputs = [{'type' : SOCKET_LOGIC_TYPE}]

        self.node = Node(self.scene, self.title, self.outputs)

    def compile(self):
        pass