import setuptools
import numpy as np
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir

# C++ pybind11 extension for player metrics
pybind11_extensions = [
    Pybind11Extension(
        "matchmaking_fast",
        ["player_metrics_fast.cpp"],
        cxx_std=17,
        # Add optimization flags
        extra_compile_args=(
            ["-O3", "-march=native", "-ffast-math"] if not get_cmake_dir() else []
        ),
    ),
]

setuptools.setup(
    ext_modules=pybind11_extensions,
    cmdclass={"build_ext": build_ext},
    include_dirs=[np.get_include()],
    zip_safe=False,
    python_requires=">=3.6",
)
