import os
from typing import Generator

from can_source.can_lexer.can_keywords import TokenType, keywords
from can_source.can_lexer.can_lexer import lexer


def cantonese_token_from_file(file: str, code: str, record_source=True) -> Generator:
    if record_source:
        os.environ[f"{file}_SOURCE"] = code
    lex: lexer = lexer(file, code, keywords)

    while True:
        with lex.get_token() as token:
            yield token
            if token.typ == TokenType.EOF:
                break
