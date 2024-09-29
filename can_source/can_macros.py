from can_source.can_ast import MacroResult
from can_source.can_lexer import can_token
from typing import List

class State:
    def __init__(self) -> None:
        self.meta_vars = {}

class CanMacro:
    def __init__(self, name, patterns, alter_blocks) -> None:
        self.name = name
        self.patterns = patterns
        self.alter_blocks = alter_blocks
        self.state = None

    def add_rule(self, pat, block):
        self.patterns.append(pat)
        self.alter_blocks.append(block)

    def try_expand(self, tokentrees: List[can_token]):
        for pat, block in zip(self.patterns, self.alter_blocks):
            if self.match_(pat, tokentrees):
                return block
        raise f"Can not expand macro: {self.name}" 

    def match_(self, tokentree, pattern: List[can_token]) -> bool:
        return True

    def eval(self, tokentrees: List[can_token]) -> MacroResult:
        block = self.try_expand(tokentrees)
        parse_res = MacroResult(block)
        return parse_res