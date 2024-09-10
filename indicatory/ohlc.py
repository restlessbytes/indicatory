import indicatory.names as names

from polars import DataFrame, col


def average_price(dataframe: DataFrame) -> DataFrame:
    """
    Calculates the average price (AP) for each row in a given DataFrame.

    Args:
        dataframe: A polars DataFrame containing "OHLC" data.

    Returns:
        The input DataFrame with an additional column named ``names.avg_price()`` that contains the
        average price for each row.
    """
    return dataframe.with_columns(
        ((col.Open + col.High + col.Low + col.Close) / 4.0).alias(names.avg_price())
    )


def naive_heikin_ashi(dataframe: DataFrame) -> DataFrame:
    """
    Implements Heikin-Ashi candles for a given DataFrame containing financial data.

    Args:
        dataframe: A polars DataFrame containing asset price data.
                   It should have columns named 'Date', 'Open', 'High', 'Low', and 'Close'.

    Returns:
        The input DataFrame with additional columns for the Heikin-Ashi open, high, low, and close
        prices (for column names, use the ``indicatory.names`` module).
    """

    # NOTE: This is a rather "naive" (i.e. un-optimized) version of Heikin-Ashi-Candles.
    records = sorted(dataframe.rows(), key=lambda record: record[0])

    dates = []
    ha_open = []
    ha_high = []
    ha_low = []
    ha_close = []
    for i in range(len(records)):
        current_record = records[i]
        if i == 0:
            # first line
            cur_date, cur_open, cur_high, cur_low, cur_close = current_record
            dates.append(cur_date)
            ha_open.append((cur_open + cur_close) / 2.0)
            ha_high.append(cur_high)
            ha_low.append(cur_low)
            ha_close.append((cur_open + cur_high + cur_low + cur_close) / 4.0)
        else:
            cur_date, cur_open, cur_high, cur_low, cur_close = current_record
            prev_open = ha_open[i - 1]
            prev_close = ha_close[i - 1]
            dates.append(cur_date)
            ha_open.append((prev_open + prev_close) / 2.0)
            ha_high.append(max(cur_high, prev_open, prev_close))
            ha_low.append(max(cur_low, prev_open, prev_close))
            ha_close.append((cur_open + cur_high + cur_low + cur_close) / 4.0)
    ha_dataframe = DataFrame(
        {
            names.DATE: dates,
            names.ha_open(): ha_open,
            names.ha_high(): ha_high,
            names.ha_low(): ha_low,
            names.ha_close(): ha_close,
        }
    )
    return dataframe.join(ha_dataframe, on=names.DATE)
