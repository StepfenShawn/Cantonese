"""Cantonese language parser/compiler with Python runtime."""

try:
    from ._core import (
        CantoneseCompileError,
        to_python,
        to_python_with_line_map,
        tokenize,
    )
except ImportError as exc:
    raise ImportError(
        "The Rust extension `cantonese_rs._core` is not built. "
        "Run `maturin develop` (or `pip install .`) to build it."
    ) from exc

# Re-export can_source functionality
from .cantonese import main as cli_main
from .error_mapper import format_cantonese_traceback, run_with_mapping
from .libs import bootstrap, get_globals, lib_env

__all__ = [
    "CantoneseCompileError",
    "to_python",
    "to_python_with_line_map",
    "tokenize",
    "cli_main",
    "format_cantonese_traceback",
    "run_with_mapping",
    "bootstrap",
    "get_globals",
    "lib_env",
]
