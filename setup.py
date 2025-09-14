import setuptools
from Cython.Build import cythonize
import numpy as np

setuptools.setup(
    ext_modules=cythonize("matchmaking/interaction_calculator.pyx"),
    include_dirs=[np.get_include()],
)
