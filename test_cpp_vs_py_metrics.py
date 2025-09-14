import pytest
import numpy as np

import matchmaking_fast as metrics_cpp
import matchmaking.metrics as metrics_py


# ------------------------------
# find_consecutive_numbers
# ------------------------------
@pytest.mark.parametrize(
    "arr,target,expected",
    [
        ([1, 1, 0, 1, 1, 1, 0], 1, [2, 3]),
        ([0, 0, 0], 1, []),
        ([1, 1, 1], 1, [3]),
        ([], 1, []),
    ],
)
def test_find_consecutive_numbers(arr, target, expected):
    py_out = metrics_py._find_consecutive_numbers(arr, target)
    cpp_out = metrics_cpp.find_consecutive_numbers(arr, target)
    assert cpp_out == py_out == expected


# ------------------------------
# count_consecutive_occurrences
# ------------------------------
@pytest.mark.parametrize(
    "symbols,expected",
    [
        (["A", "A", "A"], {"A": 2}),
        (["A", "B", "A"], {}),
        (["A", "A", "B", "B", "B"], {"A": 1, "B": 2}),
        ([], {}),
        (["X"], {}),
    ],
)
def test_count_consecutive_occurrences(symbols, expected):
    py_out = metrics_py._count_consecutive_occurences(symbols)
    cpp_out = metrics_cpp.count_consecutive_occurrences(symbols)
    assert cpp_out == py_out == expected


if __name__ == "__main__":
    pytest.main([__file__])
