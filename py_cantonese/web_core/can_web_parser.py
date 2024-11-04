import sys

from py_cantonese.can_lexer.can_lexer import *


class WebParser(object):
    def __init__(self, tokens: list, Node: list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset: int) -> list:
        if self.pos + offset >= len(self.tokens):
            return ["", ""]
        return self.tokens[self.pos + offset]

    def match(self, name: str) -> bool:
        if self.get(0)[1] == name:
            return True
        return False

    def match_type(self, name: str) -> bool:
        if self.get(0)[0] == name:
            return True
        return False

    def check(self, a, b) -> None:
        if a == b:
            return
        raise LookupError("Error Token:" + str(b))

    def skip(self, offset) -> None:
        self.pos += offset

    def run(self, Nodes: list) -> None:
        for node in Nodes:
            if node[0] == "node_call":
                web_call_new(node[1][0], node[1][1], node[2])
            if node[0] == "node_css":
                style_def(node[1][0], node[1][1], node[1][2])

    def parse(self) -> None:
        while True:
            if self.match("老作一下"):
                self.skip(1)
                self.check(self.get(0)[1], "{")
                self.skip(1)
                stmt = []
                node_main = []
                while self.tokens[self.pos][1] != "}":
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                self.skip(1)
                WebParser(stmt, node_main).parse()
                self.Node = node_main
                self.run(self.Node)
            elif self.match_type("id"):
                if self.get(1)[0] == "keywords" and self.get(1)[1] == "要点画":
                    id = self.get(0)[1]
                    self.skip(2)
                    style_stmt = []
                    node_style = []
                    while self.tokens[self.pos][1] != "搞掂":
                        style_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    self.cantonese_css_parser(style_stmt, id)
                else:
                    name = self.get(0)[1]
                    self.skip(1)
                    self.check(self.get(0)[1], "=>")
                    self.skip(1)
                    self.check(self.get(0)[1], "[")
                    self.skip(1)
                    args = []
                    while self.tokens[self.pos][1] != "]":
                        args.append(self.tokens[self.pos][1])
                        self.pos += 1
                    self.skip(1)
                    with_style = False
                    if self.match("$"):  # case 'style_with'
                        style_id = self.get(1)[1]
                        self.skip(2)
                        args.append(style_id)
                        with_style = True
                    web_ast_new(self.Node, "node_call", [name, args], with_style)
            else:
                break

    def cantonese_css_parser(self, stmt: list, id: str) -> None:
        cssParser(stmt, []).parse(id)


class cssParser(WebParser):
    def parse(self, id: str) -> None:
        while True:
            if self.match_type("id"):
                key = self.get(0)[1]
                self.skip(1)
                self.check(self.get(0)[1], "=>")
                self.skip(1)
                self.check(self.get(0)[1], "[")
                self.skip(1)
                value = []
                while self.tokens[self.pos][1] != "]":
                    value.append(self.tokens[self.pos][1])
                    self.pos += 1
                self.skip(1)
                web_ast_new(self.Node, "node_css", [id, key, value])
            else:
                break
        self.run(self.Node)


def web_ast_new(Node: list, type: str, ctx: list, with_style=True) -> None:
    Node.append([type, ctx, with_style])


def get_str(s: str) -> str:
    return eval("str(" + s + ")")


sym = {}
style_attr = {}
style_value_attr = {}

TO_HTML = "<html>\n"


def title(args: list, with_style: bool) -> None:
    global TO_HTML
    if len(args) == 1:
        t_beg, t_end = "<title>", "</title>\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        t_beg, t_end = '<title id = "' + style + '">', "</title>\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end


def h(args: list, with_style: bool) -> None:
    global TO_HTML
    if len(args) == 1:
        h_beg, h_end = "<h1>", "</h1>\n"
        TO_HTML += h_beg + get_str(args[0]) + h_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        size = "" if len(args) == 1 else args[1]
        t_beg, t_end = "<h" + size + ' id = "' + style + '">', "</h" + size + ">\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end


def img(args: list, with_style: bool) -> None:
    global TO_HTML
    if len(args) == 1:
        i_beg, i_end = "<img src = ", ">\n"
        TO_HTML += i_beg + get_str(args[0]) + i_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        i_beg, i_end = '<img id = "' + style + '" src = ', ">\n"
        TO_HTML += i_beg + get_str(args[0]) + i_end


def audio(args: list, with_style: bool) -> None:
    global TO_HTML
    if len(args) == 1:
        a_beg, a_end = "<audio src = ", "</audio>\n"
        TO_HTML += a_beg + get_str(args[0]) + a_end


def sym_init() -> None:
    global sym
    global style_attr

    sym["打标题"] = title
    sym["拎笔"] = h
    sym["睇下"] = img
    sym["Music"] = audio
    # sym['画格仔'] = table

    style_attr["要咩色"] = "color"
    style_attr["要咩背景颜色"] = "background-color"
    style_attr["要点对齐"] = "text-align"
    style_attr["要几高"] = "height"
    style_attr["要几阔"] = "width"

    style_value_attr["红色"] = "red"
    style_value_attr["黄色"] = "yellow"
    style_value_attr["白色"] = "white"
    style_value_attr["黑色"] = "black"
    style_value_attr["绿色"] = "green"
    style_value_attr["蓝色"] = "blue"
    style_value_attr["居中"] = "centre"


def head_init() -> None:
    global TO_HTML
    TO_HTML += "<head>\n"
    TO_HTML += '<meta charset="utf-8" />\n'
    TO_HTML += "</head>\n"


def web_init() -> None:
    global TO_HTML
    sym_init()
    head_init()


def web_end() -> None:
    global TO_HTML
    TO_HTML += "</html>"


style_sym = {}


def style_def(id: str, key: str, value: list) -> None:
    global style_sym
    if id not in style_sym:
        style_sym[id] = [[key, value]]
        return
    style_sym[id].append([key, value])


def style_build(value: list) -> None:
    s = ""
    for item in value:
        if (
            get_str(item[1][0]) not in style_value_attr.keys()
            and item[0] in style_attr.keys()
        ):
            s += style_attr[item[0]] + " : " + get_str(item[1][0]) + ";\n"
        elif (
            get_str(item[1][0]) not in style_value_attr.keys()
            and item[0] not in style_attr.keys()
        ):
            s += item[0] + " : " + get_str(item[1][0]) + ";\n"
        elif (
            get_str(item[1][0]) in style_value_attr.keys()
            and item[0] not in style_attr.keys()
        ):
            s += item[0] + " : " + style_value_attr[get_str(item[1][0])] + ";\n"
        else:
            s += (
                style_attr[item[0]]
                + " : "
                + style_value_attr[get_str(item[1][0])]
                + ";\n"
            )
    return s


def style_exec(sym: dict) -> None:
    global TO_HTML
    gen = ""
    s_beg, s_end = '\n<style type="text/css">\n', "</style>\n"
    for key, value in sym.items():
        gen += "#" + key + "{\n" + style_build(value) + "}\n"
    TO_HTML += s_beg + gen + s_end


def web_call_new(func: str, args_list: list, with_style=False) -> None:
    if func in sym:
        sym[func](args_list, with_style)
    else:
        func(args_list, with_style)


def get_html_file(name: str) -> str:
    return name[: len(name) - len("cantonese")] + "html"


class WebLexer(lexer):
    def __init__(self, file, code, keywords):
        super().__init__(file, code, keywords)
        (
            self.re_callfunc,
            self.re_expr,
            self.op,
            self.op_get_code,
            self.op_gen_code,
            self.build_in_funcs,
            self.bif_get_code,
            self.bif_gen_code,
        ) = ("", "", "", "", "", "", "", "")

    def get_token(self):
        self.skip_space()

        if len(self.code) == 0:
            return ["EOF", "EOF"]

        c = self.code[0]
        if self.isChinese(c) or c == "_" or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return ["keywords", token]
            return ["id", token]

        if c == "=":
            if self.check("=>"):
                self.next(2)
                return ["keywords", "=>"]

        if c in ("'", '"'):
            return ["string", self.scan_short_string()]

        if c == "." or c.isdigit():
            token = self.scan_number()
            return ["num", token]

        if c == "{":
            self.next(1)
            return ["keywords", c]

        if c == "}":
            self.next(1)
            return ["keywords", c]

        if c == "[":
            self.next(1)
            return ["keywords", c]

        if c == "]":
            self.next(1)
            return ["keywords", c]

        if c == "$":
            self.next(1)
            return ["keywords", c]

        if c == "(":
            self.next(1)
            return ["keywords", c]

        if c == ")":
            self.next(1)
            return ["keywords", c]

        self.error("睇唔明嘅Token: " + c)


def cantonese_web_run(code: str, file_name: str, open_serv=True) -> None:
    global TO_HTML
    keywords = ("老作一下", "要点画", "搞掂", "执嘢")
    lex = WebLexer(file_name, code, keywords)
    tokens = []
    while True:
        token = lex.get_token()
        tokens.append(token)
        if token == ["EOF", "EOF"]:
            break

    web_init()
    WebParser(tokens, []).parse()
    web_end()

    if style_sym != {}:
        style_exec(style_sym)
    print(TO_HTML)

    if open_serv:
        import socket

        ip_port = ("127.0.0.1", 80)
        back_log = 10
        buffer_size = 1024
        webserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webserver.bind(ip_port)
        webserver.listen(back_log)
        print("Cantonese Web Starting at 127.0.0.1:80 ...")
        while True:
            conn, addr = webserver.accept()
            recvdata = conn.recv(buffer_size)
            conn.sendall(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
            conn.sendall(bytes(TO_HTML, "utf-8"))
            conn.close()
            if input("input Y to exit:"):
                print("Cantonese Web exiting...")
                break

    else:
        f = open(get_html_file(file_name), "w", encoding="utf-8")
        f.write(TO_HTML)

    sys.exit(0)
