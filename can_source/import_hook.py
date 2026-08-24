"""Import hook that lets Python import `.cantonese` source files.

Mirrors `can_source/can_import.py` but uses the Rust compiler exposed via
`cantonese_rs._core` and injects the Cantonese runtime into imported modules.
"""

import importlib
import importlib.machinery
import os
import sys
from typing import Dict, List, Tuple

from cantonese_rs import to_python_with_line_map
from can_source.error_mapper import format_cantonese_traceback
from can_source.libs import get_globals

importlib.machinery.SOURCE_SUFFIXES.insert(0, ".cantonese")
_py_source_to_code = importlib.machinery.SourceFileLoader.source_to_code
_py_exec_module = importlib.machinery.SourceFileLoader.exec_module

# Cache of Cantonese source and line maps keyed by the .cantonese file path.
# Used by exec_module to rewrite runtime tracebacks back to Cantonese lines.
_cantonese_cache: Dict[str, Tuple[str, Dict[int, List[int]]]] = {}


def _can_source_to_code(self, data, path, _optimize=-1):
    source = data.decode("utf-8")
    if not path.endswith(".cantonese"):
        return _py_source_to_code(self, source, path, _optimize=_optimize)

    cur_file = os.environ.get("CUR_FILE", "")
    os.environ["CUR_FILE"] = path

    try:
        py_code, line_map = to_python_with_line_map(source, path)
    finally:
        os.environ["CUR_FILE"] = cur_file

    _cantonese_cache[path] = (source, line_map)
    return _py_source_to_code(self, py_code, path, _optimize=_optimize)


def _can_exec_module(self, module):
    """Execute a module, injecting the Cantonese runtime for `.cantonese` files."""
    origin = getattr(module.__spec__, "origin", "") or ""
    if origin.endswith(".cantonese"):
        module.__dict__.update(get_globals())
        try:
            return _py_exec_module(self, module)
        except Exception:
            cached = _cantonese_cache.get(origin)
            if cached is not None:
                source, line_map = cached
                exc_type, exc_value, exc_tb = sys.exc_info()
                message = format_cantonese_traceback(
                    exc_type, exc_value, exc_tb, line_map, source, origin
                )
                print(message, file=sys.stderr)
            raise

    return _py_exec_module(self, module)


importlib.machinery.SourceFileLoader.source_to_code = _can_source_to_code
importlib.machinery.SourceFileLoader.exec_module = _can_exec_module

# This is actually needed; otherwise, pre-created finders assigned to the
# current dir (i.e. `''`) in `sys.path` will not catch absolute imports of
# directory-local modules!
sys.path_importer_cache.clear()
importlib.invalidate_caches()
