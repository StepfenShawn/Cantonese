"""
    hack the python import!!!
    implement the `import *.cantonese`
"""

import importlib.machinery
import os, sys

from py_cantonese import can_parser
from py_cantonese.can_compiler.compiler import Codegen
from py_cantonese.can_lexer import can_lexer, cantonese_token_from_file
from py_cantonese.can_parser.parser_trait import new_token_context

importlib.machinery.SOURCE_SUFFIXES.insert(0, ".cantonese")
_py_source_to_code = importlib.machinery.SourceFileLoader.source_to_code


def _can_source_to_code(self, data, path, _optimize=-1):

    source = data.decode("utf-8")
    if not path.endswith(".cantonese"):
        return _py_source_to_code(self, source, path, _optimize=_optimize)

    cur_file = os.environ["CUR_FILE"]
    os.environ["CUR_FILE"] = path

    tokens = cantonese_token_from_file(path, source)
    stats = can_parser.StatParser(new_token_context(tokens)).parse_stats()
    code_gen = Codegen(stats, path=path)
    _code = code_gen.to_py()

    os.environ["CUR_FILE"] = cur_file
    return _py_source_to_code(self, _code, path, _optimize=_optimize)


importlib.machinery.SourceFileLoader.source_to_code = _can_source_to_code

#  This is actually needed; otherwise, pre-created finders assigned to the
#  current dir (i.e. `''`) in `sys.path` will not catch absolute imports of
#  directory-local modules!
sys.path_importer_cache.clear()

# Do this one just in case?
importlib.invalidate_caches()
