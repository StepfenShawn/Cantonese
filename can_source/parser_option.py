class ParserOption:
    """
    实现一个 Rust-like 嘅 `Option` 类, 用于 Parser
    """

    def __init__(self, value=None):
        self.value = value

    def is_some(self):
        return self.value is not None

    def is_none(self):
        return self.value is None

    def unwrap(self):
        if self.is_some():
            return self.value
        else:
            raise ValueError("Called `unwrap` on a `None` value.")

    def unwrap_or(self, default):
        return self.value if self.is_some() else default

    def except_(self, handler_fn):
        if self.is_none():
            handler_fn()

    def map(self, func):
        if self.is_some():
            return ParserOption(func(self.value))
        else:
            return ParserOption(None)

    def __repr__(self):
        return (
            f"Parser_Option({self.value})" if self.is_some() else "Parser_Option(None)"
        )
