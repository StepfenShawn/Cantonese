from node_graphics_socket import *

class Socket():
    def __init__(self, node, index : int = 0, position : int = LEFT_TOP, socket_type : int = SOCKET_LOGIC_TYPE, socket_name : str = '', 
                value : str = ''):
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.grSocket = QDMGraphicsSocket(self, position = position, socket_type = socket_type, socket_name = socket_name)
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position))

        self.socket_id_name = socket_name
        # 节点是否被连接?
        self.isConnected = False
        self.edges = []

        self.logic_type = 'input_type' if self.isValueInput() else 'output_type'

        self.value = value
        self.map = {}

    def getSocketPosition(self):
        ret = [None, None]
        ret[0], ret[1] = self.node.getSocketPosition(self.index, self.position)
        # 获取中心位置
        ret[0] = ret[0] + (self.grSocket.width / 2)
        ret[1] = ret[1] + (self.grSocket.height / 2)
        return ret[0], ret[1]

    def delete(self):
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket

    def isValueInput(self) -> bool:
        if self.position in (LEFT_TOP, LEFT_BOTTOM):
            return True
        else:
            return False

    def isValueOutput(self) -> bool:
        if self.position in (RIGHT_TOP, RIGHT_BOTTOM):
            return True
        else:
            return False

    def hasEdges(self):
        return len(self.edges) != 0

    def dump(self):
        value = ''
        if self.value != '':
            value = self.value
        else:
            if hasattr(self.grSocket, 'w_input'):
                if isinstance(self.grSocket.w_input, w_CheckBox):
                    if self.grSocket.w_input.isChecked():
                        value = 'True'
                    else:
                        value = 'False'
                
                elif isinstance(self.grSocket.w_input, w_input):
                    value = self.grSocket.w_input.text()
                
                else:
                    value = ''

        ret = {
            'data_type' : SOCKET_VALUE_TYPE_MAP[self.socket_type],
            'position' : self.position,
            'logic_type' : self.logic_type,
            'scoket_name' : self.socket_id_name,
            'input_value' : value,
            'status' : self.isConnected
        }

        return ret

    def load(self, obj):
        self.socket_type = obj['data_type']
        self.position = obj['position']
        self.socket_id_name = obj['socket_name']
        self.logic_type = obj['logic_type']
        self.isConnected = obj['status']
        
        try:
            if obj['input_value'] == 'True':
                value = self.grSocket.w_input.setChecked(True)
            elif obj['input_value'] == 'False':
                value = self.grSocket.w_input.setChecked(False)
            else:
                value = self.w_input.setText(obj['input_value'])
        except:
            try:
                value = self.w_input.setText(obj['input_value']) 
            except:
                pass
        return

    def getData(self):
        return self.value