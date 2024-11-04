from typing import Dict

from py_cantonese.can_macros.meta_var import MetaVar
from py_cantonese.can_lexer.can_token import can_token


class MatchState:
    def __init__(self, meta_vars: Dict[str, MetaVar]):
        self.meta_vars = meta_vars

    def update_meta_vars(self, name: str, v: can_token) -> None:
        if name in self.meta_vars:
            self.meta_vars.get(name).update(v)
        else:
            self.meta_vars[name] = MetaVar(v)
