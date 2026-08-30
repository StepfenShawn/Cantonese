"""
Map Python runtime exceptions back to Cantonese source lines.
"""

import sys
import traceback
from typing import Dict, List, Optional


def format_cantonese_traceback(
    exc_type,
    exc_value,
    exc_tb,
    line_map: Dict[int, List[int]],
    source: str,
    filename: str = "<cantonese>",
) -> str:
    """Format a Python traceback with line numbers mapped to Cantonese source."""
    source_lines = source.splitlines()
    lines = [f"Traceback (most recent call, Cantonese source {filename}):"]

    for frame, py_lineno in traceback.walk_tb(exc_tb):
        if frame.f_code.co_filename != filename:
            continue
        can_lines = line_map.get(py_lineno)
        can_lineno = can_lines[0] if can_lines else py_lineno
        can_line_text = (
            source_lines[can_lineno - 1].strip()
            if 1 <= can_lineno <= len(source_lines)
            else ""
        )
        lines.append(
            f'  File "{filename}", line {can_lineno}, in {frame.f_code.co_name}\n'
            f"    {can_line_text}"
        )

    lines.append(f"{exc_type.__name__}: {exc_value}")
    return "\n".join(lines)


def run_with_mapping(
    py_code: str,
    line_map: Dict[int, List[int]],
    source: str,
    filename: str = "<cantonese>",
    globals_dict: Optional[dict] = None,
):
    """Execute generated Python code and rewrite tracebacks to Cantonese lines.

    On error, a Cantonese-located traceback is printed to stderr and the
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
