from can_source.can_macros.match_state import MatchState
from can_source.can_error.compile_time import NoParseException, NoTokenException
from can_source.can_ast import TokenTree, MacroMetaRepExpInPat, MacroMetaId
from can_source.can_parser import *
from can_source.can_const import *


class TokenTreeHelper:
    @staticmethod
    def tree_to_list(tree: TokenTree):
        ys = [tree.open_ch]
        for leaf in tree.child:
            if isinstance(leaf, TokenTree):
                ys.extend(TokenTreeHelper.tree_to_list(leaf))
            else:
                ys.append(leaf)
        ys.append(tree.close_ch)
        return ys


class PatRuler:
    def __init__(self, pattern: list):
        self.pattern = pattern

    def with_state(self, state: MatchState) -> "Self":
        self.state = state
        return self

    def match_token(self, excepted: can_token):
        if self.state.parser_fn.match_tk(excepted):
            self.state.parser_fn.skip_once()
        else:
            raise NoParseException("NO")

    def match_meta_id(self, id: MacroMetaId):
        meta_var_name = id._id.value
        spec = FragSpec.from_can_token(id.frag_spec)
        self.state.parser_fn.start_record()

        if spec == FragSpec.IDENT:
            self.state.parser_fn.eat_tk_by_kind(TokenType.IDENTIFIER)
        elif spec == FragSpec.STMT:
            StatParser(from_=self.state.parser_fn).parse()
        elif spec == FragSpec.EXPR:
            ExpParser.from_ParserFn(self.state.parser_fn).parse_exp()
        elif spec == FragSpec.STR:
            self.state.parser_fn.eat_tk_by_kind(TokenType.STRING)
        elif spec == FragSpec.LITERAL:
            if self.state.parser_fn.match([TokenType.NUM, TokenType.STRING]):
                self.state.parser_fn.skip_once()
            else:
                raise NoParseException("No")

        self.state.update_meta_vars(meta_var_name, self.state.parser_fn.get_record())
        self.state.parser_fn.close_record()

    def match_rep(self, pat: MacroMetaRepExpInPat):

        def _run():
            for tk_node in pat.token_trees:
                self.match_pattern(tk_node)

        if pat.rep_op == RepOp.CLOSURE.value:  # *
            self.state.parser_fn.many(
                _run, util_cond=lambda: not self.state.parser_fn.match(pat.rep_sep)
            )
        elif pat.rep_op == RepOp.OPRIONAL.value:  # ?
            # self.state.parser_fn.maybe(_run, case_cond=lambda: self.state.parser_fn.match(pat.token_trees))
            pass
        elif pat.rep_op == RepOp.PLUS_CLOSE.value:  # +
            self.state.parser_fn.oneplus(
                _run, util_cond=lambda: not self.state.parser_fn.match(pat.rep_sep)
            )

    def match_pattern(self, pat) -> bool:
        try:
            if isinstance(pat, MacroMetaId):
                self.match_meta_id(pat)
            elif isinstance(pat, MacroMetaRepExpInPat):
                self.match_rep(pat)
            else:
                self.match_token(pat)
        except (NoTokenException, NoParseException):
            return False
        else:
            return True

    def match(self) -> bool:
        if len(self.pattern) == 0:
            return self.state.parser_fn.no_tokens()

        for pat in self.pattern:
            result = self.match_pattern(pat)
            if not result:
                return False

        # all pattern has been matched, it's should be `no_tokens` state
        return self.state.parser_fn.no_tokens()

    def get_state(self):
        return self.state
