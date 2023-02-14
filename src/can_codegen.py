from src.stack_vm import *

class AST(object):
    def __init__(self, Nodes) -> None:
        self.Nodes = Nodes

    def next(self, n) -> None:
        self.Nodes = self.Nodes[n : ]

    def current(self):
        if len(self.Nodes) == 0:
            return [""]
        return self.Nodes[0]

    def check(self, node, v) -> bool:
        return node[0] == v

    def run_if(self):
        elif_part = [[], [], []]
        else_part = [[], []]
        if self.current()[0] == 'node_elif':
            elif_part = self.current()
            self.next(1)
        elif self.current()[0] == 'node_else':
            else_part = self.current()
            self.next(1)
        return elif_part, else_part

    def run_except(self):
        # ["node_except", _except, except_part]
        except_part = [[], [], []]
        finally_part = [[], []]
        if self.current()[0] == 'node_except':
            except_part = self.current()
            self.next(1)
        elif self.current()[0] == 'node_finally':
            except_part = self.current()
            self.next(1)
        return except_part.finally_part


    def get_node(self) -> list:
        
        if len(self.Nodes) == 0:
            return "NODE_END"

        node = self.Nodes[0]
        
        if node[0] == 'node_print':
            self.next(1)
            return PrintStmt(node[1])

        if node[0] == 'node_let':
            self.next(1)
            return AssignStmt(node[1][1], node[2])

        if node[0] == 'node_exit':
            self.next(1)
            return ExitStmt()

        if node[0] == 'node_pass':
            self.next(1)
            return PassStmt()

        if node[0] == 'node_if':
            self.next(1)
            elif_part, else_part = self.run_if()
            return IfStmt([node[1], node[2]], [elif_part[1], elif_part[2]], \
                         [else_part[1]])

        if node[0] == 'node_try':
            self.next(1)
            except_part, finally_part = self.run_except()
            return ExceptStmt([node[1]], [except_part[1], except_part[2]], \
                            [finally_part[1]])

        if node[0] == 'node_call':
            self.next(1)
            return

        if node[0] == 'node_for':
            self.next(1)
            return ForStmt(node[1], node[2], node[3])

        if node[0] == 'node_gettype':
            self.next(1)
            return TypeStmt(node[1])

        if node[0] == 'node_loop':
            self.next(1)
            return WhileStmt(node[1], node[2])

        if node[0] == 'node_break':
            self.next(1)
            return BreakStmt()

        if node[0] == 'node_raise':
            self.next(1)
            return RaiseStmt(node[1])
        

        raise Exception("睇唔明嘅Node: " + str(node))

def make_stmt(Nodes : list, stmts : list) -> list:
    ast = AST(Nodes)
    # Get stmt from AST
    while True:
        stmt = ast.get_node()
        if stmt == "NODE_END":
            break
        stmts.append(stmt)
    return stmts

class PrintStmt(object):
    def __init__(self, expr) -> None:
        self.expr = expr
        self.type = "PrintStmt"

    def __str__(self):
        ret = "print_stmt: " + self.expr

class AssignStmt(object):
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.type = "AssignStmt"
    
class PassStmt(object):
    def __init__(self):
        self.type = "PassStmt"

class ExitStmt(object):
    def __init__(self):
        self.type = "ExitStmt"

    def __str__(self):
        return "exit_stmt"

class TypeStmt(object):
    def __init__(self, var):
        self.type = "TypeStmt"
        self.var = var

class IfStmt(object):
    def __init__(self, if_stmt, elif_stmt, else_stmt) -> None:
        self.if_stmt = if_stmt
        self.elif_stmt = elif_stmt
        self.else_stmt = else_stmt
        self.type = "IfStmt"

    def __str__(self):
        ret = "if_stmt:" + str(self.if_stmt) + \
              "elif_stmt:" + str(self.elif_stmt) + \
              "else_stmt: " + str(self.else_stmt)
        return ret

class ForStmt(object):
    def __init__(self, _iter, seq, stmt) -> None:
        self._iter = _iter
        self.seq = seq
        self.stmt = stmt
        self.type = "ForStmt"

class WhileStmt(object):
    def __init__(self, cond, stmt) -> None:
        self.cond = cond
        self.stmt = stmt
        self.type = "WhileStmt"

class BreakStmt(object):
    def __init__(self):
        self.type = "BreakStmt"

class CallStmt(object):
    def __init__(self, func, args) -> None:
        self.type = "CallStmt"

class ExceptStmt(object):
    def __init__(self, try_part, except_part, finally_part) -> None:
        self.type = "ExceptStmt"
        self.try_part = try_part
        self.except_part = except_part
        self.finally_part = finally_part

class RaiseStmt(object):
    def __init__(self, exception) -> None:
        self.type = "RaiseStmt"
        self.exception = exception

ins_idx = 0 # 指令索引
cansts_idx = 0
name_idx = 0
debug = False
    
def run_with_vm(stmts : list, gen_op_code, end, path = '', state = []) -> None:
    
    global ins_idx

    for stmt in stmts:
        if stmt.type == "PrintStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.expr))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_PRINT_ITEM", None))
        
        if stmt.type == "AssignStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.value))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NEW_NAME", stmt.key))

        if stmt.type == "PassStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NOP", None))

        if stmt.type == "IfStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.if_stmt[0]))
            s = make_stmt(stmt.if_stmt[1], [])
            # 先将要跳转的地址设置为None
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
            run_with_vm(s, gen_op_code, False, path)
            
            # TODO: need test elif stmt
            if stmt.elif_stmt != [[], []]:
                gen_op_code[start_idx - 1].set_args(ins_idx + 1)
                ins_idx += 1
                jmp_start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", None))
                ins_idx += 1
                gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST",  stmt.elif_stmt[0]))
                s = make_stmt(stmt.elif_stmt[1], [])
                ins_idx += 1
                start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
                run_with_vm(s, gen_op_code, False, path)
                gen_op_code[jmp_start_idx - 1].set_args(ins_idx - jmp_start_idx)

            elif stmt.else_stmt != [[]]:
                gen_op_code[start_idx - 1].set_args(ins_idx + 1)
                ins_idx += 1
                s = make_stmt(stmt.else_stmt[0], [])
                jmp_start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", None))
                run_with_vm(s, gen_op_code, False, path)
                gen_op_code[jmp_start_idx - 1].set_args(ins_idx - jmp_start_idx)

            else:
                gen_op_code[start_idx - 1].set_args(ins_idx)
        
        if stmt.type == "ForStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", 
                    stmt.seq[stmt.seq.index("(") + 1 : stmt.seq.index(",")]))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", 
                    stmt.seq[stmt.seq.index(",") + 1 : stmt.seq.index(")")]))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_CALL_FUNC", "range"))

        if stmt.type == "TypeStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.var))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_CALL_FUNC", "type"))
            

        if stmt.type == "WhileStmt":
            current_idx = ins_idx
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.cond))
            s = make_stmt(stmt.stmt, [])
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_TRUE", None))
            run_with_vm(s, gen_op_code, False, path)
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_JMP_ABSOLUTE", current_idx))
            gen_op_code[start_idx - 1].set_args(ins_idx)

        if stmt.type == "BreakStmt":
            ins_idx += 1
            # TODO: implement the break stmt
            gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", 1))

        if stmt.type == "RaiseStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_RAISE", eval(stmt.exception[1])))

    if end:
        ins_idx += 1
        gen_op_code.append(Instruction(ins_idx, "OP_RETURN", None)) # 结尾指令