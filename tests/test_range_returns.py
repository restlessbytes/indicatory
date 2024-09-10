import indicatory.ranges_returns as rr
import indicatory.names as names

from polars import DataFrame


def test_daily_returns():
    test_data = DataFrame(
        {names.OPEN: [2.0, 1.0, 1.0, 1.5, 4.0], names.CLOSE: [2.5, 1.0, 0.5, 1.0, 9.0]}
    )
    result = rr.daily_returns(test_data)
    assert tuple(result[names.dret()]) == (0.5, 0.0, -0.5, -0.5, 5.0)
    assert tuple(result[names.dret_pct()]) == (
        25.0,
        0.0,
        -50.0,
        -33.333333333333337,
        125.0,
    )


def test_daily_range():
    test_data = DataFrame(
        {names.HIGH: [2.5, 1.0, 1.0, 1.5, 9.0], names.LOW: [2.0, 1.0, 0.5, 0.5, 3.5]}
    )
    result = rr.daily_range(test_data)
    assert tuple(result[names.dran()]) == (0.5, 0.0, 0.5, 1.0, 5.5)
    assert tuple(result[names.dran_pct()]) == (
        25.0,
        0.0,
        100.0,
        200.0,
        157.14285714285717,
    )


def test_true_ranges():
    test_data = DataFrame(
        {
            names.HIGH: [49.2, 49.35, 49.92, 50.19, 50.12],
            names.LOW: [48.94, 48.86, 49.5, 49.87, 49.2],
            names.CLOSE: [49.07, 49.32, 49.91, 50.13, 49.53],
        }
    )
    expected_tr = (0.26, 0.49, 0.6, 0.32, 0.93)
    result = rr.true_range(test_data)
    assert tuple(result[names.tr()]) == expected_tr
    assert "Previous Close" not in result.columns


def test_average_true_range():
    test_data = DataFrame(
        {
            names.HIGH: [49.2, 49.35, 49.92, 50.19, 50.12],
            names.LOW: [48.94, 48.86, 49.5, 49.87, 49.2],
            names.CLOSE: [49.07, 49.32, 49.91, 50.13, 49.53],
        }
    )
    expected_atr = (None, None, None, 0.45, 0.61)
    result = rr.average_true_range(test_data, window_size=3)
    assert tuple(result[names.atr(3)]) == expected_atr
