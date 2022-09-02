from node import *
from node_socket import *
from node_graphics_socket import *
from res.setting import LanguageSetter

class _NodeOutput(Node):
    def __init__(self, scene):
        self.scene = scene
        self.title = LanguageSetter("cn").read()['NodeOutputName']
        self.inputs = [{'type' : SOCKET_LOGIC_TYPE}, {'type' : SOCKET_VALUE_TYPE_STRING, 'name' : "参数", "value" : "hello world"}]
        self.outputs = [{'type' : SOCKET_LOGIC_TYPE}]
        self.node_type = NODE_FUNC_TYPE
        self.node = Node(self.scene, self.title, inputs = self.inputs, outputs = self.outputs, node_type = self.node_type)

    def _compile(self):
        self.args = self.node.inputs[1].getData()
        print(self.node.inputs[1])
        if self.node.inputs[1].dump()['data_type'] == 'SOCKET_VALUE_TYPE_STRING':
            self.args = "'" + self.args + "'"
        return "print(" + self.args + ")"