"""
    将从Rust返回的dict对象转换为can_ast中定义的对象
"""

from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass

from py_cantonese.can_ast import *
from py_cantonese.can_ast.can_exp import *
from py_cantonese.can_ast.can_stat import *


@dataclass
class Position:
    """代码位置信息"""
    line: int
    column: int
    offset: int
    
    @classmethod
    def from_dict(cls, pos_dict: Dict[str, Any]) -> 'Position':
        """从字典创建Position对象"""
        if not pos_dict:
            return cls(0, 0, 0)
        return cls(
            line=pos_dict.get('line', 0),
            column=pos_dict.get('column', 0),
            offset=pos_dict.get('offset', 0)
        )


@dataclass
class Span:
    """代码范围信息"""
    start: Position
    end: Position
    
    @classmethod
    def from_dict(cls, span_dict: Dict[str, Any]) -> 'Span':
        """从字典创建Span对象"""
        if not span_dict:
            return cls(Position(0, 0, 0), Position(0, 0, 0))
        return cls(
            start=Position.from_dict(span_dict.get('start', {})),
            end=Position.from_dict(span_dict.get('end', {}))
        )


def convert_pos(span_dict: Optional[Dict[str, Any]]) -> Any:
    """
    将span字典转换为pos对象
    目前简单返回Span对象，可以根据需要调整返回类型
    """
    if not span_dict:
        return None
    return Span.from_dict(span_dict)


def convert_expression(exp_dict: Dict[str, Any]) -> Exp:
    """
    将dict表示的表达式转换为can_ast.Exp对象
    """
    exp_type = exp_dict["type"]
    
    if exp_type == "NullExp":
        return NullExp()
    
    elif exp_type == "TrueExp":
        return TrueExp()
    
    elif exp_type == "FalseExp":
        return FalseExp()
    
    elif exp_type == "NumeralExp":
        return NumeralExp(val=exp_dict["val"])
    
    elif exp_type == "StringExp":
        return StringExp(s=exp_dict["s"])
    
    elif exp_type == "IdExp":
        return IdExp(name=exp_dict["name"])
    
    elif exp_type == "ListExp":
        elem_exps = [convert_expression(elem) for elem in exp_dict["elem_exps"]]
        return ListExp(elem_exps=elem_exps)
    
    elif exp_type == "MapExp":
        elem_exps = [convert_expression(elem) for elem in exp_dict["elem_exps"]]
        return MapExp(elem_exps=elem_exps)
    
    elif exp_type == "UnopExp":
        return UnopExp(
            op=exp_dict["op"],
            exp=convert_expression(exp_dict["exp"])
        )
    
    elif exp_type == "BinopExp":
        return BinopExp(
            op=exp_dict["op"],
            exp1=convert_expression(exp_dict["exp1"]),
            exp2=convert_expression(exp_dict["exp2"])
        )
    
    elif exp_type == "FuncCallExp":
        return FuncCallExp(
            prefix_exp=convert_expression(exp_dict["prefix_exp"]),
            args=[convert_expression(arg) for arg in exp_dict["args"]]
        )
    
    elif exp_type == "ObjectAccessExp":
        return ObjectAccessExp(
            prefix_exp=convert_expression(exp_dict["prefix_exp"]),
            key_exp=convert_expression(exp_dict["key_exp"])
        )
    
    elif exp_type == "ListAccessExp":
        return ListAccessExp(
            prefix_exp=convert_expression(exp_dict["prefix_exp"]),
            key_exp=convert_expression(exp_dict["key_exp"])
        )
    
    else:
        # 对于未实现的表达式类型，返回一个标识符表达式
        return IdExp(name=f"未实现的表达式类型: {exp_type}")


def convert_statement(stat_dict: Dict[str, Any]) -> Stat:
    """
    将dict表示的语句转换为can_ast.Stat对象
    """
    stat_type = stat_dict["type"]
    
    if stat_type == "CallStat":
        return CallStat(
            exp=convert_expression(stat_dict["exp"]), 
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "AssignStat":
        return AssignStat(
            var_list=[convert_expression(var) for var in stat_dict["var_list"]],
            exp_list=[convert_expression(exp) for exp in stat_dict["exp_list"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "IfStat":
        return IfStat(
            if_exp=convert_expression(stat_dict["if_exp"]),
            if_block=[convert_statement(stmt) for stmt in stat_dict["if_block"]],
            elif_exps=[convert_expression(exp) for exp in stat_dict["elif_exps"]],
            elif_blocks=[
                [convert_statement(stmt) for stmt in block] 
                for block in stat_dict["elif_blocks"]
            ],
            else_blocks=[convert_statement(stmt) for stmt in stat_dict["else_blocks"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "PrintStat":
        return PrintStat(
            args=[convert_expression(arg) for arg in stat_dict["args"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "FunctionDefStat":
        return FunctionDefStat(
            name_exp=convert_expression(stat_dict["name_exp"]),
            args=[convert_expression(arg) for arg in stat_dict["args"]],
            blocks=[convert_statement(block) for block in stat_dict["blocks"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "ForEachStat":
        return ForEachStat(
            id_list=[convert_expression(id_exp) for id_exp in stat_dict["id_list"]],
            exp_list=[convert_expression(exp) for exp in stat_dict["exp_list"]],
            blocks=[convert_statement(block) for block in stat_dict["blocks"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "WhileStat":
        return WhileStat(
            cond_exp=convert_expression(stat_dict["cond_exp"]),
            blocks=[convert_statement(block) for block in stat_dict["blocks"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    elif stat_type == "ReturnStat":
        return ReturnStat(
            exps=[convert_expression(exp) for exp in stat_dict["exps"]],
            pos=convert_pos(stat_dict.get("span"))
        )
    
    else:
        # 对于未实现的语句类型，返回一个Pass语句
        return PassStat(pos=convert_pos(stat_dict.get("span")))


def convert_program(program_list: List[Dict[str, Any]]) -> List[Stat]:
    """
    将dict列表表示的程序转换为can_ast.Stat列表
    """
    return [convert_statement(stmt) for stmt in program_list] 