from setuptools import setup
import io

with io.open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    long_description=long_description
)