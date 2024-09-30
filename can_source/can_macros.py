from can_source.util.option import Option
from can_source.can_ast import MacroResult
from can_source.can_lexer import can_token
from can_source.can_parser import *
from can_source.can_const import *
from can_source.parser_base import ParserFn, new_token_context
from typing import List

def match(pattern, tokentrees) -> Option:
    matched_meta_vars = {}
    curF = ParserFn(ctx=new_token_context(tokentrees))
    while pattern:
        pat = pattern.pop(0)
        if isinstance(pat, can_ast.MacroMetaId):
            if FragSpec.from_ast(pat.frag_spec) == FragSpec.IDENT:
                curF.eat_tk_by_kind()
            elif FragSpec.from_ast(pat.frag_spec) == FragSpec.STMT:
                pass
            elif FragSpec.from_ast(pat.frag_spec) == FragSpec.EXPR:
                pass
        elif isinstance(pat, can_ast.MacroMetaExp):
            pass
        else:
            if curF.match_tk(pat):
                curF.skip_once()
            else:
                return Option(None)


class CanMacro:
    def __init__(self, name, patterns, alter_blocks) -> None:
        self.name = name
        self.patterns = patterns
        self.alter_blocks = alter_blocks

    def try_expand(self, tokentrees: List[can_token]):
        for pat, block in zip(self.patterns, self.alter_blocks):
            if self.match_(pat, tokentrees):
                return block
        raise f"Can not expand macro: {self.name}"

    def match_(self, pattern: List[can_token], tokentree) -> bool:
        return match(pattern, tokentree).is_some()

    def eval(self, tokentrees: List[can_token]) -> MacroResult:
        block = self.try_expand(tokentrees)
        parse_res = MacroResult(block)
        print(parse_res)
        return parse_res
