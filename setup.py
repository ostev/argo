from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Hello world app',
    ext_modules=cythonize("line_follower.py"),
    zip_safe=False,
)
