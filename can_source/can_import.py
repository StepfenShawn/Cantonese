"""
    hack the python import!!!
    implement the `import *.cantonese`
"""

import os
import importlib

from can_source import can_lexer, can_parser
from can_source.can_compile import Codegen
from can_source.parser_trait import new_token_context

importlib.machinery.SOURCE_SUFFIXES.insert(0, ".cantonese")
_py_source_to_code = importlib.machinery.SourceFileLoader.source_to_code


def _can_source_to_code(self, data, path, _optimize=-1):

    source = data.decode("utf-8")
    if not path.endswith(".cantonese"):
        return _py_source_to_code(self, source, path, _optimize=_optimize)

    cur_file = os.environ["CUR_FILE"]
    os.environ["CUR_FILE"] = path

    tokens = can_lexer.cantonese_token(path, source)
    stats = can_parser.StatParser(new_token_context(tokens)).parse_stats()
    code_gen = Codegen(stats, path=path)
    _code = code_gen.to_py()

    os.environ["CUR_FILE"] = cur_file
    return _py_source_to_code(self, _code, path, _optimize=_optimize)


importlib.machinery.SourceFileLoader.source_to_code = _can_source_to_code
