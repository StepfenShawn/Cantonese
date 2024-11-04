from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="cantonese_ast_rs",
    version="0.1.0",
    rust_extensions=[RustExtension("cantonese_ast_rs", binding=Binding.PyO3)],
    zip_safe=False,
) 