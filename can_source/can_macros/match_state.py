from typing import Dict

from can_source.can_macros.meta_var import MetaVar
from can_source.can_lexer.can_token import can_token


class MatchState:
    def __init__(self, meta_vars: Dict[str, MetaVar]):
        self.meta_vars = meta_vars

    def update_meta_vars(self, name: str, v: can_token) -> None:
        if name in self.meta_vars:
            self.meta_vars.get(name).add_matched_value(v)
        else:
            self.meta_vars[name] = MetaVar(v)
