import re
import sys

keyword = {
    "PRINT"     : "畀我睇下",
    "ENDPRINT"  : "点样先",
    "ASSIGN"    : "讲嘢",
    "EXIT"      : "同我躝",
    "IS"        : "系",
    "ISNOT"     : "唔系",
    "IF"        : "如果",
    "THEN"      : "嘅话",
    "DO"        : "->",
    "BEGIN"     : "{",
    "END"       : "}",
    "TRUE"      : "啱",
    "FALSE"     : "唔啱",
    "NONE"      : "冇",
    "WHILEDO"   : "落操场玩跑步",
    "WHILE"     : "玩到",
    "WHILEEND"  : "为止",
    "CALL"      : "用下",
    "IMPORT"    : "使下",
    "IN"        : "喺",
    "FUNCEND"   : "搞掂",
    "FUNCBEGIN" : "要做咩",
    "AND"       : "同埋"
}

build_in_func = {
    "GETTIME"   : "宜家几点",
    "RANDOM"    : "求其啦",
    "SLEEP"     : "训",
    "APPEND"    : "加啲",
    "REMOVE"    : "摞走",
    "GETLEN"    : "嘅长度",
    "TWO_SECS"  : "阵先",
    "INPUT"     : "畀你"
}
def trans(code, rep):
    for r in rep:
        code = code.replace(r[0], r[1])
    return code
    
def contonese_run(code):
    keywords_replace = [
               # Keywords for contonese
               [keyword["PRINT"] , "print"], 
               [keyword["ENDPRINT"] , "endprint"], 
               [keyword["EXIT"], "exit"], 
               [keyword["ASSIGN"], "assign"], 
               ["收工", "exit"], 
               ["辛苦晒啦", "exit"], 
               [keyword["ISNOT"], "is not"],
               [keyword["IS"], "is"], 
               [keyword["IF"], "if"], 
               [keyword["THEN"],"then"], 
               [keyword["DO"], "do"], 
               [keyword["BEGIN"], "begin"],
               [keyword["END"], "end"],
               [keyword["FUNCBEGIN"], "funcbegin"],
               [keyword["FUNCEND"], "funcend"], 
               [keyword["TRUE"], "True"], 
               [keyword["FALSE"], "False",], 
               [keyword["NONE"], "None"],
               [keyword["WHILEDO"], "while_do"], 
               [keyword["WHILE"], "while"],  
               [keyword["WHILEEND"], "whi_end"],
               ["$", "function"],
               ["就", "is"],
               [keyword["AND"], "and"],
               [keyword["CALL"], "call"], 
               [keyword["IMPORT"], "import"],
               [keyword["IN"], "in"]
            ]
    build_in_func_repl = [
        [build_in_func["INPUT"], "input"],
        # Datetime library
        [build_in_func["GETTIME"], "datetime.datetime.now()"],
        # Random library
        [build_in_func["RANDOM"], "random.random()"],
        # Time library
        [build_in_func["SLEEP"], "sleep"],
        [build_in_func["TWO_SECS"], "2"],
        # List
        [build_in_func["APPEND"], "append"],
        [build_in_func["REMOVE"], "remove"],
        [build_in_func["GETLEN"], ".__len__()"]
    ]
    tokens = []
    for token in contonese_token(code):
        tokens.append(token)
    for i in range(len(tokens)):
        if tokens[i][0] != 'string':
            tokens[i][1] = trans(tokens[i][1], keywords_replace)
            tokens[i][1] = trans(tokens[i][1], build_in_func_repl)
    contonese_parser = Parser(tokens, [])
    contonese_parser.parse()
    run(contonese_parser.Node, False)

def contonese_token(code):
    keywords = r'(?P<keywords>(畀我睇下){1}|(点样先){1}|(收工){1}|(喺){1}|' \
               r'(讲嘢){1}|(系){1})|(如果){1}|(嘅话){1}|(->){1}|({){1}|(}){1}|(同埋){1}|' \
               r'(落操场玩跑步){1}|(\$){1}|(用下){1}|(使下){1}|(要做咩){1}|(搞掂){1}|(就){1}|' \
               r'(玩到){1}|(为止){1}'
    op =  r'(?P<op>\+\+|\+=|\+|--|-=|-|\*=|/=|/|%=|%)'
    num = r'(?P<num>\d+)'
    ID =  r'(?P<ID>[a-zA-Z_][a-zA-Z_0-9]*)'
    string = r'(?P<string>\"([^\\\"]|\\.)*\")'
    expr = r'(?P<expr>[|](.*?)[|])'
    callfunc = r'(?P<callfunc>[&](.*?)[)])'
    build_in_funcs = r'(?P<build_in_funcs>(宜家几点){1}|(求其啦){1}|(训){1}|(加啲){1}|(摞走){1}|(嘅长度){1}|(阵先){1}|' \
                     r'(畀你){1})'
    patterns = re.compile('|'.join([keywords, ID, num, op, string, expr, callfunc, build_in_funcs]))
    for match in re.finditer(patterns, code):
        yield [match.lastgroup, match.group()]

def node_print_new(Node, arg):
    Node.append(["node_print", arg])

def node_sleep_new(Node, arg):
    Node.append(["node_sleep", arg])

def node_exit_new(Node):
    Node.append(["node_exit"])

def node_let_new(Node, key ,value):
    Node.append(["node_let", key, value])

def node_if_new(Node, cond, stmt):
    Node.append(["node_if", cond, stmt])

def node_loop_new(Node, cond, stmt):
    Node.append(["node_loop", cond, stmt])

def node_func_new(Node, func_name, args, body):
    Node.append(["node_fundef", func_name, args, body])

# TODO: Add args
def node_call_new(Node, func_name):
    Node.append(["node_call", func_name])

def node_build_in_func_call_new(Node, var, func_name, args):
    Node.append(["node_bcall", var, func_name, args])

def node_import_new(Node, name):
    Node.append(["node_import", name])

class Parser(object):
    def __init__(self, tokens, Node):
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset):
        if self.pos + offset >= len(self.tokens):
            return ["", ""]
        return self.tokens[self.pos + offset]
    
    def get_value(self, token):
        if token[0] == 'expr':
            # If is expr, Remove the "|"
            token[1] = token[1][1 : -1]
        if token[0] == 'callfunc':
            # If is call func, Remove the '&'
            token[1] = token[1][1 :]
        return token

    def last(self, offset):
        return self.tokens[self.pos - offset]
    
    def skip(self, offset):
        self.pos += offset
    
    def match(self, name):
        if self.get(0)[1] == name:
            self.pos += 1
            return True
        else:
            return False
    
    def match_type(self, type):
        if self.get(0)[0] == type:
            self.pos += 1
            return True
        else:
            return False
    # TODO: Add error check
    def parse(self):
        while True:
            if self.match("print"):
                node_print_new(self.Node, self.get_value(self.get(0)))
                self.skip(2) # Skip the args and end_print
            elif self.match("sleep"):
                node_sleep_new(self.Node, self.get(0))
                self.skip(1)
            elif self.match("exit"):
                node_exit_new(self.Node)
                self.skip(1)
            elif self.match("assign") and self.get(1)[1] == 'is':
                node_let_new(self.Node, self.get_value(self.get(0)), self.get_value(self.get(2)))
                self.skip(3)
            elif self.match("if"):
                cond = self.get(0)
                self.skip(4) # Skip the "then", "do", "begin"
                stmt = []
                while self.tokens[self.pos][1] != "end":
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                node_if = []
                Parser(stmt, node_if).parse()
                node_if_new(self.Node, cond, node_if)
                self.skip(1) # Skip the "end"
            elif self.match("while_do"):
                stmt = []
                while self.tokens[self.pos][1] != "while":
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                node_while = []
                self.skip(1)
                cond = self.get_value(self.get(0))
                Parser(stmt, node_while).parse()
                node_loop_new(self.Node, cond, node_while)
                self.skip(2) # Skip the "end"
            elif self.match("function"):
                if self.get(1)[0] == 'expr':
                   func_name = self.get(0)
                   args = self.get_value(self.get(1))
                   self.skip(3)
                   func_stmt = []
                   while self.tokens[self.pos][1] != "funcend":
                       func_stmt.append(self.tokens[self.pos])
                       self.pos += 1
                   node_func = []
                   Parser(func_stmt, node_func).parse()
                   node_func_new(self.Node, func_name, args, node_func)
                   self.skip(1) # Skip the funcend
                else:
                    func_name = self.get(0)
                    self.skip(2) # Skip the funcbegin
                    func_stmt = []
                    while self.tokens[self.pos][1] != "funcend":
                        func_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    node_func = []
                    Parser(func_stmt, node_func).parse()
                    node_func_new(self.Node, func_name, "None", node_func)
                    self.skip(1) # Skip the funcend
            elif self.match("call"):
                node_call_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            elif self.match("import"):
                node_import_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            elif self.match_type("expr") or self.match_type("ID"):
                if self.get(1)[0] != 'keywords' or self.get(1)[0] != 'callfunc':
                    args = self.get_value(self.get(1))
                else:
                    args = None
                node_build_in_func_call_new(self.Node, self.get_value(self.get(-1)), self.get_value(self.get(0)), args)
                self.skip(2)
            else:
                break

variable = {}
TO_PY_CODE = ""
# TODO: Build a simple vm for Contonese  
def run(Nodes, to_py, TAB = '', label = ''):
    def check(tab):
        if label != 'whi_run' and label != 'if_run':
            tab = ''
    global TO_PY_CODE
    if Nodes == None:
        return None
    for node in Nodes:
        if node[0] == "node_print":
            if to_py:
                check(TAB)
                TO_PY_CODE += TAB + "print(" + node[1][1] + ")\n"
            else:
                 exec("print(" + node[1][1] + ")", variable)
        if node[0] == "node_sleep":
            if to_py:
                check(TAB)
                TO_PY_CODE += TAB + "time.sleep(" + node[1][1] + ")\n"
            else:
                exec("time.sleep(" + node[1][1] + ")", variable)
        if node[0] == "node_import":
            if to_py:
                check(TAB)
                TO_PY_CODE += TAB + "import " + node[1][1] + "\n"
            else:
                exec("import " + node[1][1], variable)
        if node[0] == "node_exit":
            if to_py:
                check(TAB)
                TO_PY_CODE += TAB + "exit()\n"
            else:
                exec("exit()")
        if node[0] == "node_let":
            if to_py:
                check(TAB)
                TO_PY_CODE += TAB + node[1][1] + "=" + node[2][1] + "\n"
            elif node[2][0] == 'num':
                variable[node[1][1]] = int(node[2][1])
            elif node[2][0] == 'callfunc' or node[2][0] == 'expr':
                variable[node[1][1]] = eval(node[2][1], variable)
            else:
                variable[node[1][1]] = node[2][1]
        if node[0] == "node_if":
             if to_py:
                TO_PY_CODE += TAB + "if " + node[1][1] + ":\n"
                run(node[2], True, '\t', 'if_run')
             else:
                if eval(node[1][1][1 : -1], variable):
                    run(node[2], False)
        if node[0] == "node_loop":
            if to_py:
                TO_PY_CODE += TAB + "while " + node[1][1] + ":\n"
                run(node[2], True, '\t', 'whi_run')
            else:
                while eval(node[1][1], variable):
                    run(node[2], False)
        if node[0] == "node_fundef":
            run(node[3], True)
            stmt_code = TO_PY_CODE
            #stmt_code = stmt_code.replace("\n", "\n\t")
            TO_PY_CODE = ""
            # check if has args
            if node[2] == 'None':
                exec("def " + node[1][1] + "():\n\t" + stmt_code, variable)
            else:
                exec("def " + node[1][1] + "(" + node[2][1] + "):\n\t" + stmt_code, variable)
        if node[0] == "node_call":
            exec(node[1][1], variable)
        if node[0] == "node_bcall":
            exec(node[1][1] + "." + node[2][1] + "(" + node[3][1] + ")", variable)

def main():
    if len(sys.argv) == 2:
        # If a filename has been specified, we try to run it.
        try:
            with open(sys.argv[1], encoding = "utf-8") as f:
                code = f.read()
            # Skip the comment
            code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
            contonese_run(code)
        except FileNotFoundError:
            print("搵唔到你嘅文件 :(")
    else:
        print("你想点啊! Please input your filename!")

if __name__ == '__main__':
    main()