from node_graphics_socket import SOCKET_LOGIC_TYPE


class Eval(object):
    def __init__(self, node) -> None:
        self.node = node

    def trans(self):
        node_info = self.node.getAttr()
        if node_info['node_type'] == 'NODE_NONE':
            return
        elif node_info['node_type'] == 'NODE_FUNC':
            return node_info['node_name'] + '(' + self.getSockets() +')'

    def getSockets(self):
        ret = []

        for s in self.node.getAttr()['socket']['input']:
            if s['data_type'] == SOCKET_LOGIC_TYPE:
                pass
            else:
                ret.append(str(s['input_value']))

        if len(ret) == 1:
            return ret[0]