import indicatory.names as names

from itertools import product
from polars import DataFrame, Series, col


def simple_moving_average(
    dataframe: DataFrame, column_name: str = names.CLOSE, window_size: int = 10
) -> DataFrame:
    """
    Calculates the simple moving average (SMA) for a given DataFrame column and window size.

    Args:
        dataframe (DataFrame): The input DataFrame containing financial data.
        column_name (str, optional): The name of the column to calculate the SMA on. Default is "Close".
        window_size (int, optional): The number of periods to use for calculating the SMA. Default is 10.

    Returns:
        DataFrame: A new DataFrame with an additional column containing the calculated Simple Moving Average.
    """
    return dataframe.with_columns(
        (col(column_name).rolling_mean(window_size=window_size)).alias(
            names.sma(column_name=column_name, window_size=window_size)
        )
    )


def simple_moving_averages(
    dataframe: DataFrame,
    window_sizes: list[int] | None = None,
    column_names: list[str] | None = None,
) -> DataFrame:
    """
    Calculates simple moving averages for multiple columns and window sizes on a given DataFrame.

    Args:
        dataframe: The input DataFrame containing financial data.
        window_sizes: A list of different window sizes to use for calculating the SMAs.
                      If ``None``, default is ``[10]``.
        column_names: A list of columns names on which to calculate the SMAs.
                      If ``None``, defaults to ``["Close"]``.

    Returns:
        A new DataFrame with additional columns containing the calculated Simple Moving Averages
        for each combination of column and window size.
    """

    if not window_sizes:
        window_sizes = [10]
    if not column_names:
        column_names = [names.CLOSE]
    combinations = product(column_names, window_sizes)
    return dataframe.with_columns(
        *(
            (col(column_name).rolling_mean(window_size=window_size)).alias(
                names.sma(column_name=column_name, window_size=window_size)
            )
            for column_name, window_size in combinations
        )
    )


def exponential_moving_average(
    dataframe: DataFrame, column_name: str = "Close", window_size: int = 10
) -> Series:
    """
    Calculates the exponential moving average (EMA) for a given DataFrame column and window size.

    Args:
        dataframe: The input DataFrame containing financial data.
        column_name: The name of the column to calculate the EMA on. Default is "Close".
        window_size: The number of periods to use for calculating the EMA. Default is 10.

    Returns:
        A new Series containing the calculated Exponential Moving Average.
    """
    # TODO
    raise NotImplementedError()


def moving_average_convergence_divergence(
    dataframe: DataFrame, short: int = 10, long: int = 20, signal: int = 5
) -> DataFrame:
    """
    Calculates the Moving Average Convergence Divergence (MACD) for a given DataFrame and parameters.

    Args:
        dataframe: The input DataFrame containing financial data.
        short: The window size for the short period SMA used in MACD calculation. Default is 10.
        long: The window size for the long period SMA used in MACD calculation. Default is 20.
        signal: The number of periods to use for calculating the signal line
                (or moving average of MACD). Default is 5.

    Returns:
        A new DataFrame with additional columns containing the calculated MACD and its signal line.
    """
    dataframe_with_smas = simple_moving_averages(
        dataframe=dataframe, column_names=[names.CLOSE], window_sizes=[short, long]
    )
    # Define column names here in order to make things a bit more readable
    sma_short_col = names.sma(names.CLOSE, short)
    sma_long_col = names.sma(names.CLOSE, long)
    macd_col = names.macd(short_window=short, long_window=long)
    sig_col = names.macd_sig(window_size=signal)
    macd = dataframe_with_smas.with_columns(
        (col(sma_short_col) - col(sma_long_col)).alias(macd_col)
    )
    macd = macd.with_columns(
        (col(macd_col).rolling_mean(window_size=signal)).alias(sig_col)
    )
    return macd.with_columns((col(macd_col) - col(sig_col)))


def moving_median(
    dataframe: DataFrame, column_name: str = names.CLOSE, window_size: int = 10
):
    """
    Calculates the moving median (MM) for a given DataFrame column and window size.

    Args:
        dataframe: The input DataFrame containing financial data.
        column_name: The name of the column to calculate the Moving Median on. Default is "Close".
        window_size: The number of periods to use for calculating the Moving Median. Default is 10.

    Returns:
        A new DataFrame with an additional column containing the calculated Moving Median.
    """
    return dataframe.with_columns(
        (col(column_name).rolling_median(window_size=window_size)).alias(
            names.mm(column_name=column_name, window_size=window_size)
        )
    )
