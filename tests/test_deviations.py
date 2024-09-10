import indicatory.names as names

from polars import DataFrame
from indicatory.deviations import (
    standard_deviation,
    standard_deviation_bands,
    mean_absolute_deviation,
    average_absolute_deviation,
    average_absolute_deviation_bands,
)

TEST_DATA = DataFrame({"A": [1.0, 2.0, 4.0, 9.0]})
STANDARD_DEVIATIONS = (None, 0.7071067811865476, 1.4142135623730951, 3.5355339059327378)
AVG_ABS_DEVIATIONS = (None, 0.5, 1.0, 2.5)


def test_standard_deviation():
    result = standard_deviation(TEST_DATA, window_size=2, column_name="A")[
        names.sd("A", 2)
    ]
    assert tuple(result) == STANDARD_DEVIATIONS


def test_standard_deviation_bands():
    result = standard_deviation_bands(TEST_DATA, window_size=2, column_name="A")
    lower_expected = (None, 1.2928932188134525, 2.585786437626905, 5.464466094067262)
    upper_expected = (None, 2.7071067811865475, 5.414213562373095, 12.535533905932738)
    assert tuple(result[names.sd_lower("A", 2)]) == lower_expected
    assert tuple(result[names.sd_upper("A", 2)]) == upper_expected


def test_mean_absolute_deviation():
    assert mean_absolute_deviation(TEST_DATA["A"]) == 2.5


def test_average_absolute_deviation():
    result = average_absolute_deviation(TEST_DATA, window_size=2, column_name="A")[
        names.aad("A", 2)
    ]
    assert tuple(result) == AVG_ABS_DEVIATIONS


def test_average_absolute_deviation_bands():
    result = average_absolute_deviation_bands(TEST_DATA, window_size=2, column_name="A")
    lower_expected = (None, 1.5, 3.0, 6.5)
    upper_expected = (None, 2.5, 5.0, 11.5)
    assert tuple(result[names.aad_lower("A", 2)]) == lower_expected
    assert tuple(result[names.aad_upper("A", 2)]) == upper_expected
