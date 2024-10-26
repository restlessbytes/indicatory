import numpy as np
import polars

import indicatory.names as names

from polars import DataFrame, Series, col
from indicatory.means_medians import (
    simple_moving_average,
    simple_moving_averages,
)

# I'm defining the names of those columns as local constants in this module since
# they're not used anywhere else
GAINS_COL = "Gains"
LOSSES_COL = "Losses"


def percentage_price_oscillator(
    dataframe: DataFrame,
    short_window_size: int = 10,
    long_window_size: int = 20,
) -> DataFrame:
    """
    Calculates Percentage Price Oscillator (PPO) for a given dataframe with financial data ("OHLC").

    Args:
        dataframe: The input dataframe with financial data. It should contain at least one column
                   named 'Close' which represents the closing price of the asset.
        short_window_size: Size of the window for calculating short moving average. Defaults to 10.
        long_window_size: Size of the window for calculating long moving average. Defaults to 20.

    Returns:
        A new dataframe with added column representing PPO.
    """
    close_column = names.CLOSE
    short_col = names.sma(column_name=close_column, window_size=short_window_size)
    long_col = names.sma(column_name=close_column, window_size=long_window_size)
    ppo_col = names.ppo(
        column_name=close_column,
        short_window_size=short_window_size,
        long_window_size=long_window_size,
    )
    return (
        # Start with SMAs with window sizes "short" and "long"
        simple_moving_averages(
            dataframe=dataframe,
            window_sizes=[short_window_size, long_window_size],
            column_names=[close_column],
        )
        .with_columns(
            # Calculate Percentage Price Oscillator (based on short / long SMAs)
            (((col(short_col) - col(long_col)) / col(long_col)) * 100).alias(ppo_col)
        )
        # Drop columns for short and long SMAs since they were only needed to calculate PPO
        .drop([short_col, long_col])
    )


def _gains(close_vals: polars.Series) -> float:
    previous_close = close_vals.item(0)
    current_close = close_vals.item(-1)
    return max(current_close - previous_close, 0.0)


def _losses(close_vals: polars.Series) -> float:
    previous_close = close_vals.item(0)
    current_close = close_vals.item(-1)
    return max(previous_close - current_close, 0.0)


def _moving_gains_and_losses(dataframe: DataFrame) -> DataFrame:
    # NOTE: Gains and losses are *absolute* (i.e. positive) values
    return dataframe.with_columns(
        # Column 'Gains'
        col.Close.rolling_map(_gains, window_size=2)
        .fill_null(value=0.0)
        .alias(GAINS_COL),
        # Column 'Losses'
        col.Close.rolling_map(_losses, window_size=2)
        .fill_null(value=0.0)
        .alias(LOSSES_COL),
    )


def _simple_moving_average_gains_and_losses(
    dataframe: DataFrame, window_size: int = 10
) -> DataFrame:
    dataframe_with_gains_and_losses = _moving_gains_and_losses(dataframe)
    return simple_moving_averages(
        dataframe=dataframe_with_gains_and_losses,
        window_sizes=[window_size],
        column_names=[GAINS_COL, LOSSES_COL],
    )


def _calculate_current_average_gains_losses(
    current_value: float, previous_average: float, window_size: int
) -> float:
    return (previous_average * (window_size - 1) + current_value) / window_size


def _calculate_moving_average_gains_losses(s: Series, window_size: int) -> Series:
    results = []
    for i in range(s.count()):
        if i < window_size - 1:
            results.append(None)
        elif i == window_size - 1:
            results.append(s[:window_size].mean())
        else:
            new_average = _calculate_current_average_gains_losses(
                current_value=s[i],
                previous_average=results[i - 1],
                window_size=window_size,
            )
            results.append(new_average)
    return Series(results)


def _exponential_moving_average_gains_and_losses(
    dataframe: DataFrame, window_size: int = 10
) -> DataFrame:
    # Let n = window_size, gains = values of column 'Gains', losses = values of column 'Losses'.
    # The first n values of gains and losses are calculated as a simple average.
    # After that, each new value is calculated as such:
    #   new_avg_gains = (prev_avg_gains * (n-1) + cur_gains) / n
    #   new_avg_losses = (prev_agv_loss * (n-1) + cur_loss) / n
    dataframe_with_gains_and_losses = _moving_gains_and_losses(dataframe)
    ema_gains = _calculate_moving_average_gains_losses(
        s=dataframe_with_gains_and_losses[GAINS_COL], window_size=window_size
    )
    ema_losses = _calculate_moving_average_gains_losses(
        s=dataframe_with_gains_and_losses[LOSSES_COL], window_size=window_size
    )
    return dataframe.with_columns(
        ema_gains.alias(names.ema(GAINS_COL, window_size)),
        ema_losses.alias(names.ema(LOSSES_COL, window_size)),
    )


def _relative_strength_index(
    moving_average_gains_and_losses: DataFrame,
    window_size: int,
    gains_col: str,
    losses_col: str,
) -> DataFrame:
    rs_col = names.rs(window_size=window_size)
    # TODO Drop 'intermediate' columns?
    return moving_average_gains_and_losses.with_columns(
        # Calculate Relative Strength = (SMA gains) / (SMA losses)
        (col(gains_col) / col(losses_col))
        .alias(rs_col)
        # 'Cast' division errors ("divide-by-zero") and "null' values to zero
        .fill_nan(value=0.0)
        .fill_null(value=0.0)
        .replace(old=np.inf, new=0.0)
    ).with_columns(
        # Convert Relative Strength values to a "Relative Strength Index" between 0 and 100
        (100.0 - (100.0 / (1.0 + col(rs_col)))).alias(names.rsi(window_size))
    )


def simple_relative_strength_index(
    dataframe: DataFrame, window_size: int = 10
) -> DataFrame:
    """
    Calculates a "simpler" version of the Relative Strength Index (RSI) for a given dataframe
    of financial data ("OHLC").

    More specifically, this version uses simple moving averages for smoothing instead of exponential
    smoothing factors.

    For more information, see `Cutler's RSI <https://en.wikipedia.org/wiki/Relative_strength_index#Cutler's_RSI>`_

    Args:
        dataframe: The input dataframe with financial data. It should contain at least two columns named
                   'Gains' and 'Losses', which represent the gains and losses of the asset respectively.
        window_size: Size of the window for calculating Exponential Moving Average. Defaults to 10.

    Returns:
        A new dataframe with added column representing RSI values.
    """
    # https://en.wikipedia.org/wiki/Relative_strength_index#Cutler's_RSI
    gains_col = names.sma(GAINS_COL, window_size)
    losses_col = names.sma(LOSSES_COL, window_size)
    moving_average_gains_and_losses = _simple_moving_average_gains_and_losses(
        dataframe=dataframe, window_size=window_size
    )
    return _relative_strength_index(
        moving_average_gains_and_losses=moving_average_gains_and_losses,
        window_size=window_size,
        gains_col=gains_col,
        losses_col=losses_col,
    )


def relative_strength_index(dataframe: DataFrame, window_size: int = 10):
    """
    Calculates the Relative Strength Index (RSI) for a given dataframe of financial data ("OHLC").

    Args:
        dataframe: The input dataframe with financial data. It should contain at least two
                   columns named 'Gains' and 'Losses', which represent the gains and losses
                   of the asset respectively.
        window_size: Size of the window for calculating Exponential Moving Average. Defaults to 10.

    Returns:
        A new dataframe with added column representing RSI values.
    """
    gains_col = names.ema(GAINS_COL, window_size)
    losses_col = names.ema(LOSSES_COL, window_size)
    moving_average_gains_and_losses = _exponential_moving_average_gains_and_losses(
        dataframe=dataframe, window_size=window_size
    )
    return _relative_strength_index(
        moving_average_gains_and_losses=moving_average_gains_and_losses,
        window_size=window_size,
        gains_col=gains_col,
        losses_col=losses_col,
    )


def stochastic_oscillator(dataframe: DataFrame, window_size: int = 5):
    """
    Calculates the Stochastic Oscillator (SO) for a given dataframe of financial data.

    Args:
        dataframe: The input dataframe with financial data. It should contain at least
                   three columns named 'Close', 'High' and 'Low', which represent the closing price,
                   highest price and lowest price of the security respectively.
        window_size: Size of the window for calculating rolling min/max and moving average. Defaults to 5.

    Returns:
            DataFrame with added columns representing "fast" (Fast %K, Fast %D) and "slow" (Slow %K, Slow %D)
            stochastic oscillators.
    """
    # Explanation: Stochastic oscillators, fast and slow
    #  Fast %K = %K basic calculation
    #  Fast %D = N-period SMA of Fast %K
    #          = SMA_N(Fast %K)
    #  Slow %K = Fast %K smoothed with N-period SMA
    #          = SMA_N(Fast %K)
    #          = Fast %D
    #  Slow %D = N-period SMA of Slow %K
    #          = SMA_N(Slow %K)
    #          = SMA_N(Fast %D)
    #          = SMA_N(SMA_N(Fast %K))

    # Column names
    low_window = f"Low {window_size}"
    high_window = f"High {window_size}"
    fast_k = names.fast_k(window_size)
    fast_d = names.fast_d(window_size)
    slow_k = names.slow_k(window_size)
    slow_d = names.slow_d(window_size)

    # Calculate the lowest low and highest high over last 'n' days
    dataframe = dataframe.with_columns(
        [
            col(names.LOW).rolling_min(window_size=window_size).alias(low_window),
            col(names.HIGH).rolling_max(window_size=window_size).alias(high_window),
        ]
    )

    # Calculate Fast %K
    dataframe = dataframe.with_columns(
        (
            (col(names.CLOSE) - col(low_window))
            / (col(high_window) - col(low_window))
            * 100
        ).alias(fast_k)
    )

    # Calculate Fast %D
    dataframe = dataframe.with_columns(
        col(fast_k).rolling_mean(window_size=window_size).alias(fast_d)
    )

    # Calculate Slow %K (= Fast %D)
    dataframe = dataframe.with_columns(col(fast_d).alias(slow_k))

    # Calculate Slow %D (= SMA_N(Slow %K))
    return dataframe.with_columns(
        col(slow_k).rolling_mean(window_size=window_size).alias(slow_d)
    )


def column_difference(dataframe: DataFrame, column_1: str, column_2: str) -> DataFrame:
    """
    Calculate the "Column Difference" (CDF) for two given columns in a dataframe.

    The CDF is simply the result of subtracting the values in column ``column_2`` from
    the values in column ``column_1``.

    Args:
        dataframe: A (polars) DataFrame containing time series data (OHLC + indicators).
        column_1: The name of the column whose values act as *minuends*.
        column_2: The name of the column whose values act as *subtrahends*.

    Returns:
        A new (polars) DataFrame with an additional column containing the result of
        subtracting the values in column ``column_2`` from the values in column
        ``column_1``.
    """
    return dataframe.with_columns(
        (col(column_1) - col(column_2)).alias(
            names.cdf(column_1=column_1, column_2=column_2)
        )
    )


def detrended_price_oscillator(
    dataframe: DataFrame, price_column: str = names.CLOSE, window_size: int = 10
) -> DataFrame:
    """
    Calculate the Detrended Price Oscillator (DPO) for a given column in a dataframe.

    The DPO is computed as the difference between the simple moving average of the
    price and the "current price", shifted by a "half the window size plus one" period.

    Args:
        dataframe: A (polars) DataFrame containing time series data (OHLC + indicators).
        price_column: The name of the column to calculate DPO on; defaults to 'CLOSE'.
        window_size: The size of the moving window for calculating averages; defaults to 10 periods.

    Returns:
        A new (polars) DataFrame with an additional column containing the calculated DPO values.
    """
    shift = int(window_size / 2.0) + 1
    return simple_moving_average(
        dataframe=dataframe, window_size=window_size, column_name=price_column
    ).with_columns(
        (
            col(price_column).shift(shift)
            - col(names.sma(column_name=price_column, window_size=window_size))
        ).alias(names.dpo(column_name=price_column, window_size=window_size))
    )


def rate_of_change(dataframe: DataFrame, column: str) -> DataFrame:
    """
    Calculate the Rate of Change (ROC) for a given column in a Polars dataframe.

    The ROC is computed as the difference ("change") between the current and
    previous value in the specified column. It therefore measures the absolute
    change between two data points, not a relative one.

    Args:
        dataframe: A (polars) DataFrame containing the time series data.
        column: The name of the column to calculate ROC on.

    Returns:
        A new Polars DataFrame with two additional columns containing the calculated
        ROC values + "ROC as percentage".
    """
    roc_column = names.roc(column)
    roc_pct_column = names.roc_pct(column)
    result = dataframe.with_columns(
        (col(column) - col(column).shift(1)).alias(roc_column)
    ).with_columns(
        (((col(column) - col(column).shift(1)) / col(column).shift(1)) * 100.0)
        .round(5)
        .alias(roc_pct_column)
    )
    return result
