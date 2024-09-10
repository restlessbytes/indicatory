import polars

import indicatory.names as names

from polars import DataFrame, Series, col, when


def daily_returns(dataframe: DataFrame) -> DataFrame:
    """
     Calculates the daily returns ("Close" - "Open") and percentage change in the closing price for a given
     dataframe of financial data ("OHLC").

    Args:
        dataframe: The input dataframe with financial data. It should contain at least
                   two columns named 'Close' and 'Open', which represent the closing and opening
                   prices of the security respectively.

    Returns:
        A new dataframe with added columns representing daily return and percentage change in price (use module
        ``indicatory.names`` for column names).
    """
    return dataframe.with_columns(
        (col(names.CLOSE) - col(names.OPEN)).alias(names.dret()),
        (((col(names.CLOSE) / col(names.OPEN)) - 1.0) * 100.0).alias(names.dret_pct()),
    )


def daily_range(dataframe: DataFrame) -> DataFrame:
    """
     Calculates the daily range ("High" - "Low") and percentage change for a given dataframe of financial data.

    Args:
        dataframe: The input dataframe with financial data. It should contain at least two columns
                   named 'High' and 'Low', which represent the highest and lowest prices of the security respectively.

    Returns:
        DataFrame with added columns representing daily range and percentage change in price (use module
        ``indicatory.names`` for column names).
    """
    return dataframe.with_columns(
        (col(names.HIGH) - col(names.LOW)).alias(names.dran()),
        (((col(names.HIGH) / col(names.LOW)) - 1.0) * 100.0).alias(names.dran_pct()),
    )


def true_range(dataframe: DataFrame, round_to_decimals: int = 5) -> DataFrame:
    """
     Calculates the true range (TR) for a given dataframe of financial data.

     True range is defined as the greatest of three values: current high less the current low, absolute value
     of current high less the previous close, and absolute value of current low less the previous close.

    Args:
        dataframe: The input dataframe with financial data. It should contain at least three columns
                   named 'High', 'Low' and 'Close', which represent the highest price, lowest price and closing price
                   of the security respectively.
        round_to_decimals: Number of decimal places to which the true range values will be rounded. Defaults to 5.

    Returns:
        DataFrame with an added column representing true range ('TR').
    """
    prev_close = "Previous Close"
    return (
        dataframe.with_columns(col.Close.shift(1).alias(prev_close))
        .with_columns(
            when(col(prev_close).is_null())
            .then(col.High - col.Low)
            .otherwise(
                polars.max_horizontal(
                    col.High - col.Low,
                    abs(col.High - col(prev_close)),
                    abs(col.Low - col(prev_close)),
                )
            )
            .round(round_to_decimals)
            .alias(names.tr())
        )
        .drop(prev_close)
    )


def _calculate_current_average_true_range(
    previous_avg_true_range: float, current_true_range: float, window_size: int
) -> float:
    return (
        previous_avg_true_range * (window_size - 1) + current_true_range
    ) / window_size


def _calculate_average_true_ranges(
    true_ranges: Series, window_size: int, round_to_decimals: int = 5
) -> Series:
    # https://en.wikipedia.org/wiki/Average_true_range#Calculation
    atr = []
    for i in range(true_ranges.count()):
        if i < window_size:
            atr.append(None)
        elif i == window_size:
            # The initial ATR is just mean(TR) of the first "window_size" number of items
            atr.append(true_ranges[:window_size].mean())
        else:
            # After that, the ATR is calculated as:
            #  ATR(cur) = (prev_ATR * (window_size - 1) + cur_TR) / window_size
            current_atr = _calculate_current_average_true_range(
                previous_avg_true_range=atr[i - 1],
                current_true_range=true_ranges[i],
                window_size=window_size,
            )
            atr.append(current_atr)
    return Series(atr).round(round_to_decimals)


def average_true_range(
    dataframe: DataFrame, window_size: int = 10, round_to_decimals: int = 5
) -> DataFrame:
    """
    Calculates the Average True Range (ATR) and its percentage change over the closing price
    for a given dataframe of financial data.

    Args:
        dataframe: The input dataframe with financial data. It should contain at least three columns
                   named 'Close', 'High' and 'Low', which represent the closing price, highest price
                   and lowest price of the security respectively.
        window_size: Size of the rolling window used for calculating the ATR. Defaults to 10.
        round_to_decimals: Number of decimal places to which the ATR values will be rounded. Defaults to 5.

    Returns:
        DataFrame with added columns representing average true range and percentage change in price (use module
       ``indicatory.names`` for column names).
    """
    dataframe_with_tr = true_range(dataframe=dataframe)
    return dataframe_with_tr.with_columns(
        _calculate_average_true_ranges(
            true_ranges=dataframe_with_tr[names.tr()],
            window_size=window_size,
            round_to_decimals=round_to_decimals,
        ).alias(names.atr(window_size=window_size))
    ).with_columns(
        ((col(names.atr(window_size)) / col.Close) * 100.0).alias(
            names.atr_pct(window_size)
        )
    )
