import indicatory.names as names

from polars import DataFrame
from indicatory.ohlc import average_price
from datetime import datetime

OHLC_TEST_DATES = [
    datetime(2024, 8, 1, 8, 0),
    datetime(2024, 8, 2, 8, 0),
    datetime(2024, 8, 3, 8, 0),
    datetime(2024, 8, 4, 8, 0),
    datetime(2024, 8, 5, 8, 0),
]
OHLC_TEST_DATAFRAME = DataFrame(
    {
        names.DATE: OHLC_TEST_DATES,
        names.OPEN: [58.67, 57.46, 56.37, 55.98, 54.79],
        names.HIGH: [58.82, 57.72, 56.88, 56.09, 55.03],
        names.LOW: [57.03, 56.21, 55.35, 54.17, 52.32],
        names.CLOSE: [57.73, 56.27, 56.81, 54.17, 53.83],
    }
)


def test_mean_pricing():
    expected_mean_prices = [
        58.0625,
        56.915000000000006,
        56.3525,
        55.102500000000006,
        53.99249999999999,
    ]
    result = average_price(OHLC_TEST_DATAFRAME)[names.avg_price()]
    assert tuple(result) == tuple(expected_mean_prices)
