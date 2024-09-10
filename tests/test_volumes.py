import indicatory.names as names

from datetime import datetime, timedelta
from polars import DataFrame, Series, col
from indicatory.volumes import on_balance_volume, price_by_volume


def test_on_balance_volumes():
    start_date = datetime(2010, 10, 27, 8, 0)
    dates = [start_date + timedelta(days=n) for n in range(0, 10)]
    input_dataframe = DataFrame(
        {
            names.DATE: dates,
            names.CLOSE: [
                53.26,
                53.3,
                53.32,
                53.72,
                54.19,
                53.92,
                54.65,
                54.6,
                54.21,
                54.53,
            ],
            names.VOLUME: [0, 82, 81, 83, 89, 92, 133, 103, 99, 101],
        }
    )
    obv_series_expected = Series(
        names.obv(), [0, 82, 163, 246, 335, 243, 376, 273, 174, 275]
    )
    result = on_balance_volume(input_dataframe)
    assert result.select(col(names.obv())).to_series().equals(obv_series_expected)


def test_price_by_volume():
    test_data = DataFrame(
        {
            names.CLOSE: [4.0, 1.5, 3.0, 9.0, 5.5],
            names.VOLUME: [12_123, 15_932, 24_923, 9_004, 4_200],
        }
    )
    result = price_by_volume(test_data)
    assert tuple(result[names.pv(names.CLOSE)]) == (
        3030.75,
        10621.333333333334,
        8307.666666666666,
        1000.4444444444445,
        763.6363636363636,
    )
