from distutils.core import Extension, setup
from Cython.Build import cythonize

ext = [
    Extension("compiler.keywords", sources=["compiler/keywords.pyx"]),
    Extension("compiler.can_lexer", sources=["compiler/can_lexer.pyx"]),
    Extension("compiler.parser_base", sources=["compiler/parser_base.pyx"]),
    Extension("compiler.util", sources=["compiler/util.pyx"]),
    Extension("compiler.can_parser", sources=["compiler/can_parser.pyx"]),
    Extension("compiler.can_compile", sources=["compiler/can_compile.pyx"]),

]

setup(ext_modules=cythonize(ext, build_dir="./cython_build", language='c++'))