"""
    hack the python import!!!
    implement the `import *.cantonese`
"""

import importlib.machinery
import os, sys

from cantonese_rs import parse_to_ast
from py_cantonese.can_ast.can_ast_converter import convert_program
from py_cantonese.can_compiler.compiler import Codegen

importlib.machinery.SOURCE_SUFFIXES.insert(0, ".cantonese")
_py_source_to_code = importlib.machinery.SourceFileLoader.source_to_code


def _can_source_to_code(self, data, path, _optimize=-1):

    source = data.decode("utf-8")
    if not path.endswith(".cantonese"):
        return _py_source_to_code(self, source, path, _optimize=_optimize)

    cur_file = os.environ["CUR_FILE"]
    os.environ["CUR_FILE"] = path

    # 使用Rust解析器生成AST的dict表示
    ast_dict = parse_to_ast(source)
    
    if isinstance(ast_dict, list):
        # 将dict表示转换为can_ast对象
        stats = convert_program(ast_dict)

        # 使用转换后的can_ast对象生成Python代码
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
