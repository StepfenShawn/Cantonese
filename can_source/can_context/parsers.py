from typing import TypeVar, Any, List
from can_source.can_lexer.can_token import can_token
from can_source.can_parser.parser_trait import ParserFn, new_token_context

Parser = TypeVar("Parser")


class CanParserContext:
    """
    A class to hold state of `parsers` in `compile-time`
    """

    def __init__(self):
        self.parser = None

    def with_name(self, name: str):
        if name == "macro_body":
            from can_source.can_parser import MacroBodyParser

            self.parser = MacroBodyParser
        elif name == "macro_pat":
            from can_source.can_parser import MacroPatParser

            self.parser = MacroPatParser
        elif name == "exp":
            from can_source.can_parser import ExpParser

            self.parser = ExpParser
        elif name == "stat":
            from can_source.can_parser import StatParser

            self.parser = StatParser
        else:
            raise Exception("Unreachable!!!")
        return self

    def with_tokens(self, tokens: List[can_token]):
        self.fn = ParserFn(new_token_context((token for token in tokens)))
        if hasattr(self.parser, "from_ParserFn"):
            self.parser = self.parser.from_ParserFn(self.fn)
        else:
            self.parser = self.parser(from_=self.fn)
        return self

    def parse(self, name: str = "parse") -> Any:
        return getattr(self.parser, name)()

    def can_be_parse_able(self, name: str = "parse") -> bool:
        getattr(self.parser, name)()
        return self.fn.no_tokens()
