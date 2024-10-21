from typing import TypeVar, Any
from can_source.can_parser.parser_trait import ParserFn

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

    def with_fn(self, fn: ParserFn):
        if hasattr(self.parser, "from_ParserFn"):
            self.parser = self.parser.from_ParserFn(fn)
        else:
            self.parser = self.parser(from_=fn)
        return self

    def parse(self) -> Any:
        return self.parser.parse()
