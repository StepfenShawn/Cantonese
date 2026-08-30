"""
Import hook that lets Python import `.cantonese` source files.
"""

import importlib
import importlib.machinery
import os
import sys
from typing import Dict, List, Tuple

from ._core import compile_with_diagnostics, to_python_with_line_map
from .error_mapper import format_cantonese_traceback
from .libs import get_globals

importlib.machinery.SOURCE_SUFFIXES.append(".cantonese")
_py_source_to_code = importlib.machinery.SourceFileLoader.source_to_code
_py_exec_module = importlib.machinery.SourceFileLoader.exec_module

# Cache of Cantonese source and line maps keyed by the .cantonese file path.
# Used by exec_module to rewrite runtime tracebacks back to Cantonese lines.
_cantonese_cache: Dict[str, Tuple[str, Dict[int, List[int]]]] = {}


class _CantoneseShadowFinder:
    """Meta path finder that prevents .cantonese files from shadowing .py files.

    When both foo.py and foo.cantonese exist somewhere in sys.path,
    ``import foo`` will load foo.py instead of foo.cantonese.  This avoids
    circular-import errors when a Cantonese source file has the same stem as
    a standard-library module (e.g. ``random.cantonese`` vs ``random.py``).
    """

    def find_spec(self, fullname, path, target=None):  # noqa: D102
        # Only intercept absolute imports from sys.path (path is None).
        if path is not None:
            return None

        # Don't interfere with modules that are already loaded.
        if fullname in sys.modules:
            return None

        parts = fullname.split(".")

        cantonese_file = None
        py_file = None

        for entry in sys.path:
            if not entry:
                entry = os.getcwd()

            base = os.path.join(entry, *parts)

            if cantonese_file is None and os.path.isfile(base + ".cantonese"):
                cantonese_file = base + ".cantonese"

            if py_file is None and os.path.isfile(base + ".py"):
                py_file = base + ".py"

        # A .cantonese file would be found AND a .py file also exists
        # somewhere in sys.path – redirect to the .py file so that the
        # standard library (or any .py module) is not shadowed.
        if cantonese_file is not None and py_file is not None:
            import importlib.util

            return importlib.util.spec_from_file_location(fullname, py_file)

        return None


# Install the shadow-guard finder *before* PathFinder so that it gets the
# first chance to resolve module names that have both .cantonese and .py
# variants in sys.path.
sys.meta_path.insert(0, _CantoneseShadowFinder())


def _can_source_to_code(self, data, path, _optimize=-1):
    source = data.decode("utf-8")
    if not path.endswith(".cantonese"):
        return _py_source_to_code(self, source, path, _optimize=_optimize)

    cur_file = os.environ.get("CUR_FILE", "")
    os.environ["CUR_FILE"] = path

    try:
        py_code, diagnostics = compile_with_diagnostics(source, path)
        if diagnostics:
            for d in diagnostics:
                print(d.render(source, colors=True), file=sys.stderr)
            raise RuntimeError(diagnostics[0].message)
        _, line_map = to_python_with_line_map(source, path)
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
