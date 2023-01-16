# The base class for all AST nodes.
class AST(object):
    def __str__(self) -> str:
        return "BaseAST\n"

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

class FuncCallExp(AST):
    def __init__(self, line : int, last_line : int, prefix_exp : AST, name_exp : AST, args : AST):
        self.line = line
        self.last_line = last_line
        self.prefix_exp = prefix_exp
        self.name_exp = name_exp
        self.args = args

    def __str__(self):
        s = ''
        s += '"PrefixExp": {\n'
        for line in str(self.prefix_exp).split('\n'):
            s += '  ' + line + '\n'
        s += '},\n'
        s += '"NameExp": ' + str(self.name_exp) + ',\n'
        s += '"Args": ' + '['
        for arg in self.args:
            s += '{\n'
            for line in str(arg).split('\n'):
                if len(line):
                    s += '  ' + line + '\n'
            s += '}'
        s += ']'
        return s


class ExitStat(AST):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "ExitStat \n"

class FuncCallStat(AST):
    def __init__(self, exp : AST):
        self.exp = exp

class IfStat(AST):
    def __init__(self, if_exps : list, if_blocks : list, elif_exps : list, 
                    elif_blocks : list, else_blocks : list):
        self.if_exps = if_exps
        self.if_blocks = if_blocks
        self.elif_exps = elif_exps
        self.elif_blocks = elif_blocks
        self.else_blocks = else_blocks

    def __str__(self) -> str:
        s = 'IfStat:\n'
        s += '"Exps": ' + '\n'
        for exp in self.if_exps:
            for l in str(exp).split('\n'):
                s += '\t' + l + '\n'
        
        s += '"if_Blocks": ' + '\n'
        for block in self.if_blocks:
            for l in str(block).split('\n'):
                s += '\t' + l + '\n'

        if (self.elif_exps != [] or self.elif_blocks != []):
            s += '"Exps": ' + '\n'
            for exp in self.elif_exps:
                for l in str(exp).split('\n'):
                    s += '\t' + l + '\n'
            
            s += '"elif_Blocks": ' + '\n'
            for block in self.elif_blocks:
                for l in str(block).split('\n'):
                    s += '\t' + l + '\n'

        if (self.else_blocks != []):
            s += '"elif_Blocks": ' + '\n'
            for block in self.else_blocks:
                for l in str(block).split('\n'):
                    s += '\t' + l + '\n'

        return s

class PrintStat(AST):
    def __init__(self, args : list):
        self.args = args

    def __str__(self) -> str:
        s = 'PrintStat:\n'
        for arg in self.args:
            for l in str(arg).split('\n'):
                s += '\t' + l + '\n'

        return s

class PassStat(AST):
    def __init__(self) -> None:
        pass

    def __str__(self):
        return 'PassStat'


"""
assignstat := '讲嘢' varlist '系' explist
            | '讲嘢' '=>' '{' assignblock '}'
"""
class AssignStat(AST):
    def __init__(self, last_line : int, var_list : AST, exp_list : AST):
        self.last_line = last_line
        self.var_list = var_list
        self.exp_list = exp_list

    def __str__(self):
        s = 'AssignStat:\n'
        s += '"VarList": ' + '\n'
        for var in self.var_list:
            for l in str(var).split('\n'):
                if len(l):
                    s += '  ' + l + '\n'

        s += '"ExpList": ' + '\n'
        for exp in self.exp_list:
            for l in str(exp).split('\n'):
                if len(l):
                    s += '  ' + l + '\n'

        return s

class ForStat(AST):
    def __init__(self, id : AST, from_exp : AST, to_exp : AST, blocks : list) -> None:
        self.var = id
        self.from_exp = from_exp
        self.to_exp = to_exp
        self.blocks = blocks

    def __str__(self) -> str:
        s = 'ForStat:\n'
        s += 'Var: ' + str(self.var) + '\n'
        s += 'From: ' + str(self.from_exp) +  '\n'
        s += 'To: ' + str(self.to_exp) + '\n'
        s += 'Block:\n'
        for block in self.blocks:
            for l in str(block).split('\n'):
                if len(l):
                    s += '\t' + l + '\n'

        return s

class WhileStat(AST):
    def __init__(self, exps : list, blocks : list) -> None:
        self.cond_exps = exps
        self.blocks = blocks

    def __str__(self) -> str:
        s = 'WhileStat:\n'
        s += 'Cond:\n'
        for cond_exp in self.cond_exps:
            for l in str(cond_exp).split('\n'):
                if len(l):
                    s += '\t' + l + '\n'
        s += 'Blocks:\n'
        for block in self.blocks:
            for l in str(block).split('\n'):
                if len(l):
                    s += '\t' + l + '\n'

        return s


class ListInitStat(AST):
    def __init__(self) -> None:
        pass

class FunctoinDefStat(AST):
    def __init__(self, name_exp : AST, args : list, blocks : list) -> None:
        self.name_exp = name_exp
        self.args = args
        self.blocks = blocks

    def __str__(self) -> str:
        s = 'FuncDefStat:\n'
        s += 'Name: ' + str(self.name_exp) + '\n'
        s += 'Args: ' + str(self.args) + '\n'
        s += 'Blocks: \n'
        for block in self.blocks:
            for l in str(block).split('\n'):
                if len(l):
                    s += '\t' + l + '\n'

class ClassDefStat(AST):
    def __init__(self) -> None:
        pass

class ImportStat(AST):
    def __init__(self, idlist : list) -> None:
        self.idlist = idlist

    def __str__(self) -> str:
        s = 'ImportStat:\n'
        for var in self.idlist:
            for l in str(var).split('\n'):
                if len(l):
                    s += '  ' + l + '\n'
        
        return s

class RaiseStat(AST):
    def __init__(self) -> None:
        pass

class TryStat(AST):
    def __init__(self) -> None:
        pass

class LambdaStat(AST):
    def __init__(self) -> None:
        pass

class GlobalStat(AST):
    def __init__(self, idlist :list) -> None:
        self.idlist = idlist

    def __str__(self):
        s = 'GlobalStat:\n'
        for var in self.idlist:
            for l in str(var).split('\n'):
                if len(l):
                    s += '  ' + l + '\n'
        
        return s

class BreakStat(AST):
    def __init__(self) -> None:
        pass

    def __str__(self):
        return "BreakStat\n"

class TypeStat(AST):
    def __init__(self, exps) -> None:
        self.exps = exps

    def __str__(self) -> str:
        pass