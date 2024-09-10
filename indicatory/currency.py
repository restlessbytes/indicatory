import indicatory.names as names

from polars import DataFrame, col


def relative_currency_strength(
    dataframe: DataFrame, currency_data: DataFrame
) -> DataFrame:
    """
    Relative Currency Strength (RCS) compares the price of an asset (open and close) to the
    strength of the currency in which it is traded.

    Args:
        dataframe: OHLC data for an asset (stock, commodity etc.).
        currency_data: OHLC data for the currency in which the asset is traded (e.g. USD for US stocks).

    Returns:
        Original dataframe with two additional columns "RSC Open" and "RSC Close", containing the RCS
        values calculated for the opening and closing prices of the asset, respectively.
    """
    start_date = dataframe[names.DATE].min()
    end_date = dataframe[names.DATE].max()
    # ensure that dataframe["Date"] and currency_data["Date"] cover the same time frame
    currency_data_slice = currency_data.filter(
        col.Date.is_between(start_date, end_date)
    )
    return dataframe.with_columns(
        (dataframe[names.OPEN] / currency_data_slice[names.OPEN]).alias(
            names.rcs_open()
        ),
        (dataframe[names.CLOSE] / currency_data_slice[names.CLOSE]).alias(
            names.rcs_close()
        ),
    )
