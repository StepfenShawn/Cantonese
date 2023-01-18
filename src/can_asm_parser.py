import sys

from can_lexer import *

TO_ASM = ""

class AsmParser(object):
    def __init__(self, tokens : list, Node : list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset : int) -> list:
        if self.pos + offset >= len(self.tokens):
            return [None, ["", ""]]
        return self.tokens[self.pos + offset]
        
    def match(self, name : str) -> bool:
        if self.get(0)[1][1] == name:
            return True
        return False
    
    def match_type(self, name : str) -> bool:
        if self.get(0)[1][0] == name:
            return True
        return False
    
    def check(self, a, b) -> None:
        if a == b:
            return
        raise LookupError("Error Token:" + str(b))

    def skip(self, offset) -> None:
            self.pos += offset

    def get_value(self, token):
        if token[1][0] == 'expr':
            # If is expr, Remove the "|"
            token[1][1] = token[1][1][1 : -1]
        if token[1][0] == 'register':
            token[1][1] = token[1][1][1 : -1]
        return token[1][1]

    def run(self, Nodes) -> None:
        global TO_ASM
        for node in Nodes:
            if node[0] == 'node_data':
                TO_ASM += "section .data\n"
                for d in node[1]:
                    TO_ASM += d[0] + " equ " + d[1] + "\n"

            if node[0] == 'node_mov':
                TO_ASM += "mov " + node[1][0] + ", " + node[1][1] + "\n"

            if node[0] == 'node_int':
                TO_ASM += "int " + node[1][0] + "\n"

            if node[0] == 'node_global':
                TO_ASM += "global " + node[1][0] + "\n"

            if node[0] == 'node_code':
                TO_ASM += node[1][0] + ":\n"
                self.run(node[1][1])

    def parse(self) -> None:
        while True:
            if self.match_type('expr'):
                if self.get(1)[1][1] == "有咩":
                    data_name = self.get(0)[1]
                    self.skip(4)
                    data_stmt = []
                    while self.tokens[self.pos][1][1] != "}":
                        data_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    ret = self.data_parse(data_stmt, data_name)
                    asm_ast_new(self.Node, "node_data", ret)
            
                if self.get(1)[1][1] == "要做咩":
                    code_name = self.get_value(self.get(0))
                    self.skip(4)
                    code_stmt = []
                    while self.tokens[self.pos][1][1] != "}":
                        code_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    stmt_node = []
                    AsmParser(code_stmt, stmt_node).parse()
                    asm_ast_new(self.Node, "node_code", [code_name, stmt_node])

                if self.get(1)[1][1] == "排头位":
                    start_name = self.get_value(self.get(0))
                    self.skip(4)
                    asm_ast_new(self.Node, "node_global", [start_name])

            elif self.match_type('register'):
                reg = self.get_value(self.get(0))
                self.skip(1)
                if self.get(0)[1][1] == "收数":
                    self.skip(2)
                    data = self.get_value(self.get(0))
                    asm_ast_new(self.Node, 'node_mov', [reg, data])
                    self.skip(1)
            
            elif self.match("仲要等埋"):
                self.skip(2)
                addr = self.get_value(self.get(0))
                asm_ast_new(self.Node, 'node_int', [addr])
                self.skip(1)

            else:
                break

    def data_parse(self, stmt, name) -> None:
        return dataParser(stmt, []).parse(name)
        
class dataParser(AsmParser):
    def parse(self, name) -> None:
        ret = []
        while True:
            if self.match_type("identifier"):
                key = self.get_value(self.get(0))
                self.skip(1)
                self.check(self.get(0)[1][1], "係")
                self.skip(1)
                val = self.get_value(self.get(0))
                self.skip(1)
                ret.append([key, val])
            else:
                break
        return ret

def asm_ast_new(Node : list, type : str, ctx : list) -> None:
    Node.append([type, ctx])

class AsmLerxer(lexer):
    def __init__(self, code, keywords, ins):
        super().__init__(code, keywords)
        self.ins = ins
        self.op, self.op_get_code, self.op_gen_code, \
        self.build_in_funcs, self.re_callfunc, self.bif_get_code, \
        self.bif_gen_code = "", "", "", "", "", "", ""
        self.re_register = r"[(](.*?)[)]"

    def scan_register(self):
        return self.scan(self.re_register)

    def get_token(self):
        # TODO
        self.skip_space()
        if len(self.code) == 0:
            return [self.line, ['EOF', 'EOF']]
        
        c = self.code[0]

        if c == '|':
           token = self.scan_expr()
           return [self.line, ['expr', token]]

        if c == '(':
            token = self.scan_register()
            return [self.line, ['register', token]]
        
        if c == '{':
            self.next(1)
            return [self.line, ['keyword', '{']]
        
        if c == '}':
            self.next(1)
            return [self.line, ['keyword', '}']]            

        if self.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return [self.line, ['keywords', token]]
            if token in self.ins:
                return [self.line, ['ins', token]]
            return [self.line, ['identifier', token]]
        
        if c in ('\'', '"'):
            return [self.line, ['string', self.scan_short_string()]]
        
        if c == '.' or c.isdigit():
            token = self.scan_number()
            return [self.line, ['num', token]]

        if c == '-':
            if self.check('->'):
                self.next(2)
                return [self.line, ['keyword', '->']]
        
        self.error("睇唔明嘅Token: " + c)

def Cantonese_asm_run(code : str, file_name : str) -> None:
    global TO_ASM

    ins_mov_from = "收数"
    ins_int = "仲要等埋"
    kw_datadef = "有咩"
    kw_secdef = "要做咩"
    kw_is = "係"
    kw_main = "排头位"
    kw_begin = "开工"

    keywords = (kw_datadef, kw_secdef,
            kw_is, kw_main, kw_begin)
    ins = (ins_mov_from, ins_int)
    lex = AsmLerxer(code, keywords, ins)
    tokens = []

    while True:
        token = lex.get_token()
        tokens.append(token)
        if token[1] == ['EOF', 'EOF']:
            break

    AST = []
    AsmParser(tokens, AST).parse()
    AsmParser(tokens, AST).run(AST)
    print(TO_ASM)
    sys.exit(1)