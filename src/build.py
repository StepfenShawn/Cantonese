from distutils.core import Extension, setup
from Cython.Build import cythonize

ext = [
    Extension("can_keywords", sources=["can_keywords.pyx"]),
    Extension("can_lexer", sources=["can_lexer.pyx"]),
    Extension("parser_base", sources=["parser_base.pyx"]),
    Extension("can_utils", sources=["can_utils.pyx"]),
    Extension("can_parser", sources=["can_parser.pyx"]),
    Extension("can_compile", sources=["can_compile.pyx"]),
]

setup(ext_modules=cythonize(ext, build_dir="./cython_build"))