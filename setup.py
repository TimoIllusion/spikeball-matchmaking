import setuptools
from Cython.Build import cythonize
import numpy as np

setuptools.setup(
    name="matchmaking",
    version="0.1.0",
    author="Timo Leitritz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_dirs=[np.get_include()],
    ext_modules=cythonize("matchmaking/interaction_calculator.pyx"),
)
