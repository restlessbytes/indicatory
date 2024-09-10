import indicatory.names as names

from datetime import date
from polars import DataFrame
from indicatory.currency import relative_currency_strength


def test_relative_currency_strength():
    asset = DataFrame(
        {
            names.DATE: [
                date(2024, 8, 5),
                date(2024, 8, 6),
                date(2024, 8, 7),
                date(2024, 8, 8),
            ],
            names.OPEN: [1, 2, 3, 4],
            names.CLOSE: [3, 2, 1, 1],
        }
    )
    currency = DataFrame(
        {
            names.DATE: [date(2024, 8, day) for day in range(1, 11)],
            names.OPEN: [0.5 for _ in range(1, 11)],
            names.CLOSE: [1.0 for _ in range(1, 11)],
        }
    )
    result = relative_currency_strength(dataframe=asset, currency_data=currency)
    assert tuple(result[names.rcs_open()]) == (2.0, 4.0, 6.0, 8.0)
    assert tuple(result[names.rcs_close()]) == (3.0, 2.0, 1.0, 1.0)
