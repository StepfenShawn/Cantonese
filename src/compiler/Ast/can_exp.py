from .ast_base import AST

# none
class NullExp(AST):
    def __init__(self, line : int) -> None:
        self.line = line

# true
class TrueExp(AST):
    def __init__(self, line : int) -> None:
        self.line = line


# false
class FalseExp(AST):
    def __init__(self, line : int) -> None:
        self.line = line

# <*>
class VarArgExp(AST):
    def __init__(self, line : int) -> None:
        self.line = line

    def __str__(self) -> str:
        return "Line: %s\n <*>" % str(self.line)

# Numeral
class NumeralExp(AST):
    def __init__(self, line : int, val) -> None:
        self.line = line
        self.val = val

    def __str__(self):
        return "NumeralExp:\n Val: %s\n" % str(self.val)

# <->
class ConcatExp(AST):
    def __init__(self, line : int, exps : AST) -> None:
        self.line = line
        self.exps = exps

    def __str__(self) -> str:
        s = "ConcatExp:\n"
        s += '"Exps": ' + '\n'
        for exp in self.exps:
            for l in str(exp).split('\n'):
                s += '\t' + l + '\n'
        return s

# Literal String
class StringExp(AST):
    def __init__(self, line : int, s : str) -> None:
        self.line = line
        self.s = s
    
    def __str__(self):
        return "StringExp:\n String: %s\n" % self.s

# List Expr
class ListExp(AST):
    def __init__(self, elem_exps : list) -> None:
        self.elem_exps = elem_exps

    def __str__(self) -> str:
        s = 'ListExp:\n'
        for elem_exp in self.elem_exps:
            for l in str(elem_exp).split('\n'):
                if len(l):
                    s += '\t' + l + '\n'
        return s

# Map Expr
class MapExp(AST):
    def __init__(self, elem_exps : list) -> None:
        self.elem_exps = elem_exps

    def __str__(self) -> str:
        s = 'MapExp:\n'
        for elem_exp in self.elem_exps:
            for l in str(elem_exp).split('\n'):
                if len(l):
                    s += '\t' + l + '\n'
        return s

# unop exp
class UnopExp(AST):
    def __init__(self, line : int, op, exp : AST) -> None:
        self.line = line
        self.op = op
        self.exp = exp

    def __str__(self):
        s = ''
        s += 'Op: ' + str(self.op) + '\n'
        s += 'Exp: ' + '\n'
        for l in str(self.exp).split('\n'):
            if len(l):
                s += '\t' + l + '\n'
        return s

# exp1 op exp2
class BinopExp(AST):
    def __init__(self, line : int, op, exp1 : AST, exp2 : AST):
        self.line = line
        self.op = op
        self.exp1 = exp1
        self.exp2 = exp2

    def __str__(self):
        s = ''
        s += '"Op": ' + str(self.op) + '\n'
        s += '"exp1": ' '\n'
        for l in str(self.exp1).split('\n'):
            if len(l) > 0:
                s += '  ' + l + '\n'

        s += '"exp2": ' '\n'
        for l in str(self.exp2).split('\n'):
            if len(l) > 0:
                s += '  ' + l + '\n'
        return s

# exp1 = exp2
class AssignExp(AST):
    def __init__(self, exp1 : AST, exp2 : AST) -> None:
        self.exp1 = exp1
        self.exp2 = exp2

    def __str__(self):
        s = 'AssignExp:\n'
        s += '"exp1": \n'
        for l in str(self.exp1).split('\n'):
            if len(l):
                s += '\t' + l + '\n'
        s += '"exp2": \n'
        for l in str(self.exp2).split('\n'):
            if len(l):
                s += '\t' + l + '\n'

        return s

# exp1 ==> exp2
class MappingExp(AST):
    def __init__(self, exp1 : AST, exp2 : AST) -> None:
        self.exp1 = exp1
        self.exp2 = exp2

    def __str__(self):
        s = 'MappingExp:\n'
        s += '"exp1": \n'
        for l in str(self.exp1).split('\n'):
            if len(l):
                s += '\t' + l + '\n'
        s += '"exp2": \n'
        for l in str(self.exp2).split('\n'):
            if len(l):
                s += '\t' + l + '\n'

        return s

class IdExp(AST):
    def __init__(self, line : int, name : str):
        self.line = line
        self.name = name

    def __str__(self):
        return '"Identifier": ' + '"' + self.name + '"' + "\n"


class ParensExp(AST):
    def __init__(self, exp : AST):
        self.exp = exp

class ObjectAccessExp(AST):
    def __init__(self, last_line : int, prefix_exp : AST, key_exp : AST):
        self.last_line = last_line
        self.prefix_exp = prefix_exp
        self.key_exp = key_exp

    def __str__(self):
        s = ''
        s += "ObjectAccessExp: \n"
        s += '"PrefixExp": {\n'
        for line in str(self.prefix_exp).split('\n'):
            s += '  ' + line + '\n'
        s += '},\n'
        s += '"Key": ' + str(self.key_exp) + ',\n'
        return s

class ListAccessExp(AST):
    def __init__(self, last_line : int, prefix_exp : AST, key_exp : AST):
        self.last_line = last_line
        self.prefix_exp = prefix_exp
        self.key_exp = key_exp

    def __str__(self):
        s = ''
        s += "ListAccessExp: \n"
        s += '"PrefixExp": {\n'
        for line in str(self.prefix_exp).split('\n'):
            s += '  ' + line + '\n'
        s += '},\n'
        s += '"Key": ' + str(self.key_exp) + ',\n'
        return s

class FuncCallExp(AST):
    def __init__(self, prefix_exp : AST,args : AST):
        self.prefix_exp = prefix_exp
        self.args = args

    def __str__(self):
        s = ''
        s += '"PrefixExp": {\n'
        for line in str(self.prefix_exp).split('\n'):
            s += '  ' + line + '\n'
        s += '},\n'
        s += '"Args": ' + '['
        for arg in self.args:
            s += '{\n'
            for line in str(arg).split('\n'):
                if len(line):
                    s += '  ' + line + '\n'
            s += '}'
        s += ']'
        return s

class LambdaExp(AST):
    def __init__(self, id_list : list, blocks : list) -> None:
        self.id_list = id_list
        self.blocks = blocks

    def __str__(self) -> str:
        s = 'LambdaExp:\n'
        s += 'id_list:\n'
        for id in self.id_list:
            for l in str(id).split('\n'):
                s += '\t' + l + '\n'
        s += 'blocks:\n'
        for block in self.blocks:
            for l in str(block).split('\n'):
                s += '\t' + l + '\n'

        return s

class SpecificIdExp(AST):
    def __init__(self, id : AST) -> None:
        self.id = id

    def __str__(self) -> str:
        return "SpecificIdExp\n"

class ClassSelfExp(AST):
    def __init__(self, exp : AST):
        self.exp = exp

    def __str__(self) -> str:
        s = 'ClassSelfExp:\n'
        for l in str(self.exp).split('\n'):
            s += '\t' + l + '\n'
        return s

class IfElseExp(AST):
    def __init__(self, if_cond_exp : AST, if_exp : AST, else_exp : AST) -> None:
        self.if_cond_exp = if_cond_exp
        self.if_exp = if_exp
        self.else_exp = else_exp

    def __str__(self) -> str:
        s = 'IfElseExp:\n'
        s += "IfCond:\n"
        for l in str(self.if_cond_exp).split('\n'):
            s += '\t' + l + '\n'
        s += "IfExp:\n"
        for l in str(self.if_exp).split('\n'):
            s += '\t' + l + '\n'
        s += "ElseExp:\n"
        for l in str(self.else_exp).split('\n'):
            s += '\t' + l + '\n'

        return s

class ExitStat(AST):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "ExitStat \n"