class CanTokenContext:
    """
    A class to hold state of `tokens` in `compile-time`
    """

    def __init__(self):
        pass

    def set_token_ctx(self, token_ctx: tuple):
        """
        we need a buffer_tokens in lazy parser.
        because the first token maybe not case in `look_ahead` mode.
        """
        self.tokens, self.buffer_tokens = token_ctx

    def get_token_ctx(self) -> tuple:
        return (self.tokens, self.buffer_tokens)
