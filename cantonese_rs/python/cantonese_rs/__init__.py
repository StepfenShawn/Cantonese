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

__all__ = [
    "CantoneseCompileError",
    "to_python",
    "to_python_with_line_map",
    "tokenize",
]
