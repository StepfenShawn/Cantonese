"""
Map Python runtime exceptions back to Cantonese source lines.
"""

import sys
import traceback
from typing import Dict, List, Optional

from ._core import format_runtime_diagnostic


def format_cantonese_traceback(
    exc_type,
    exc_value,
    exc_tb,
    line_map: Dict[int, List[int]],
    source: str,
    filename: str = "<cantonese>",
) -> str:
    """Format a runtime error as a Rust-style diagnostic.

    Walks the traceback to find the innermost frame that maps to a
    Cantonese source line, then renders it with the Rust diagnostic
    formatter (file location, source snippet, caret underline).
    """
    # Find the deepest frame that belongs to this Cantonese file and has a
    # valid line-map entry.
    chosen_can_line = None
    for frame, py_lineno in traceback.walk_tb(exc_tb):
        if frame.f_code.co_filename != filename:
            continue
        can_lines = line_map.get(py_lineno)
        if can_lines:
            chosen_can_line = can_lines[0]

    if chosen_can_line is None:
        # Fallback: just use the exception message.
        return f"{exc_type.__name__}: {exc_value}"

    return format_runtime_diagnostic(
        exc_type.__name__,
        '喺runtime察覺到錯誤! ' + str(exc_value),
        source,
        chosen_can_line,
        filename,
        colors=None,  # auto-detect
    )


def run_with_mapping(
    py_code: str,
    line_map: Dict[int, List[int]],
    source: str,
    filename: str = "<cantonese>",
    globals_dict: Optional[dict] = None,
):
    """Execute generated Python code and rewrite tracebacks to Cantonese lines.

    On error, a Cantonese-located diagnostic is printed to stderr and the
    original exception is re-raised.
    """
    if globals_dict is None:
        globals_dict = {}

    code_obj = compile(py_code, filename, "exec")

    try:
        exec(code_obj, globals_dict)
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        message = format_cantonese_traceback(
            exc_type, exc_value, exc_tb, line_map, source, filename
        )
        print(message, file=sys.stderr)
        raise
