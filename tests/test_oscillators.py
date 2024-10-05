from polars import DataFrame
from indicatory.oscillators import (
    _moving_gains_and_losses,
    _simple_moving_average_gains_and_losses,
    _exponential_moving_average_gains_and_losses,
    relative_strength_index,
    simple_relative_strength_index,
    detrended_price_oscillator,
    rate_of_change,
)


def test_gains_and_losses():
    test_data = DataFrame({"Close": [1.0, 2.0, 2.0, 2.5, 0.5]})
    result = _moving_gains_and_losses(test_data)
    assert tuple(result["Gains"]) == (0.0, 1.0, 0.0, 0.5, 0.0)
    assert tuple(result["Losses"]) == (0.0, 0.0, 0.0, 0.0, 2.0)

    result = _simple_moving_average_gains_and_losses(test_data, window_size=3)
    assert tuple(result["SMA 3 Gains"]) == (
        None,
        None,
        0.3333333333333333,
        0.5,
        0.16666666666666666,
    )
    assert tuple(result["SMA 3 Losses"]) == (None, None, 0.0, 0.0, 0.6666666666666666)

    result = _exponential_moving_average_gains_and_losses(test_data, window_size=3)
    assert tuple(result["EMA 3 Gains"]) == (
        None,
        None,
        0.3333333333333333,
        0.38888888888888884,
        0.25925925925925924,
    )
    assert tuple(result["EMA 3 Losses"]) == (None, None, 0.0, 0.0, 0.6666666666666666)


def test_relative_strength_indices():
    test_data = DataFrame({"Close": [0.5, 1.5, 0.5, 1.0, 2.0, 2.0, 2.5, 0.5]})

    # Simple RSI (aka "Cutler's RSI")
    result = simple_relative_strength_index(test_data, window_size=3)
    assert tuple(result["RS 3"]) == (0.0, 0.0, 1.0, 1.5, 1.5, 0.0, 0.0, 0.25)
    assert tuple(result["RSI 3"]) == (0.0, 0.0, 50.0, 60.0, 60.0, 0.0, 0.0, 20.0)

    # "Classic" RSI
    result = relative_strength_index(test_data, window_size=3)
    assert tuple(result["RS 3"]) == (
        0.0,
        0.0,
        1.0,
        1.7499999999999998,
        4.0,
        4.0,
        6.531250000000001,
        0.40347490347490356,
    )
    assert tuple(result["RSI 3"]) == (
        0.0,
        0.0,
        50.0,
        63.63636363636363,
        80.0,
        80.0,
        86.72199170124482,
        28.748280605226952,
    )


def test_detrended_price_oscillator():
    test_data = DataFrame({"A": [1.0, 2.0, 3.0, 4.0, 5.0]})
    result = detrended_price_oscillator(test_data, price_column="A", window_size=3)
    assert tuple(result["DPO 3 A"]) == (None, None, -1.0, -1.0, -1.0)


def test_rate_of_change():
    test_data = DataFrame({"A": [1.0, 2.0, 3.0, 5.0]})
    result = rate_of_change(dataframe=test_data, column="A")
    assert tuple(result["dA"]) == (None, 1.0, 1.0, 2.0)
