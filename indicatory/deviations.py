import numpy

import indicatory.names as names

from polars import DataFrame, Series, col


def standard_deviation(
    dataframe: DataFrame, window_size: int = 10, column_name: str = names.CLOSE
) -> DataFrame:
    """
    Calculates the rolling standard deviation of a specified column in a ``polars.DataFrame``.

    The rolling standard deviation is calculated over a user-specified window size.

    By default, the function uses a window size of 10 and the 'Close' column.

    Args:
        dataframe: A Polars DataFrame containing numerical data.
        window_size: An integer specifying the size of the rolling window to use for
                     calculating standard deviation. Defaults to 10.
        column_name: A string specifying the name of the column in the DataFrame to
                     calculate standard deviation on. Defaults to 'Close'.

    Returns:
        A Polars DataFrame with an additional column containing the rolling standard deviation
        values for the specified input column. The new column is named using the ``names.sd``
        function, which takes the base column name and window size as arguments. If no valid
        numerical data can be found in the specified column, the new column will contain null
        values.
    """
    return dataframe.with_columns(
        col(column_name)
        .rolling_std(window_size=window_size)
        .alias(names.sd(base_column=column_name, window_size=window_size))
    )


def variance(
    dataframe: DataFrame, window_size: int = 10, column_name: str = names.CLOSE
) -> DataFrame:
    """
    Calculates the rolling variance of a specified column in a Polars DataFrame.

    The rolling variance is calculated over a user-specified window size.

    By default, the function uses a window size of 10 and the 'Close' column.

    Args:
        dataframe: A Polars DataFrame containing numerical ("OHLC") data.
        window_size: An integer specifying the size of the rolling window to use
                     for calculating variance. Defaults to 10.
        column_name: A string specifying the name of the column in the DataFrame
                     to calculate variance on. Defaults to 'Close'.

    Returns:
        A Polars DataFrame with an additional column containing the rolling variance values for
        the specified input column. The new column is named using the ``names.var`` function,
        which takes the base column name and window size as arguments. If no valid numerical
        data can be found in the specified column, the new column will contain null values.
    """
    return dataframe.with_columns(
        col(column_name)
        .rolling_var(window_size=window_size)
        .alias(names.var(base_column=column_name, window_size=window_size))
    )


def mean_absolute_deviation(s: Series) -> float:
    """
    Calculates the mean absolute deviation of a Polars Series.

    The mean absolute deviation is calculated as the average of the absolute differences
    between each element in the series and the mean of the series.

    For more information, see `Wikipedia:MAD <https://en.wikipedia.org/wiki/Average_absolute_deviation#Mean_absolute_deviation_around_the_mean>`_

    Args:
        s: A Polars Series containing numerical ("OHLC") data.

    Returns:
        A float representing the mean absolute deviation of the input series.
    """
    return (numpy.abs(s - s.mean())).sum() / s.count()


def mean_absolute_deviation_percent(s: Series) -> float:
    """
    Calculates the mean absolute deviation of a Polars Series as a percentage.

    It's calculated as the mean absolute deviation of ``s`` divided by the mean of ``s``
    (times 100, since it's a percentage).

    Args:
        s: A Polars Series containing numerical ("OHLC") data.

    Returns:
        A float representing the mean absolute deviation of the input series as a percentage.
    """
    return (mean_absolute_deviation(s) / s.mean()) * 100.0


def average_absolute_deviation(
    dataframe: DataFrame, window_size: int = 10, column_name: str = names.CLOSE
):
    """
    Calculates the Average Absolute Deviation as the rolling Mean Absolute Deviation of a
    specified column in a Polars DataFrame.

    The rolling mean absolute deviation is calculated over a user-specified window size
    using `indicatory.deviations.mean_absolute_deviation`.

    For more information, see `Wikipedia:AAD <https://en.wikipedia.org/wiki/Average_absolute_deviation>`_


    Args:
        dataframe: A Polars DataFrame containing numerical ("OHLC") data.
        window_size: An integer representing the size of the rolling window. Defaults to 10.
        column_name: A string representing the name of the column to calculate the rolling mean absolute
                     deviation on. Defaults to 'Close'.

    Returns:
        A Polars DataFrame with an additional column containing the rolling mean absolute
        deviation values for the specified input column. The new column is named using the
        `names.aad` function, which takes the base column name and window size as arguments. If
        no valid numerical data can be found in the specified column, the new column will
        contain null values.
    """
    return dataframe.with_columns(
        (
            col(column_name).rolling_map(
                mean_absolute_deviation, window_size=window_size
            )
        ).alias(names.aad(base_column=column_name, window_size=window_size))
    ).with_columns(
        (
            col(column_name).rolling_map(
                mean_absolute_deviation_percent, window_size=window_size
            )
        ).alias(names.aad_pct(base_column=column_name, window_size=window_size))
    )


def standard_deviation_bands(
    dataframe: DataFrame, window_size: int = 10, column_name: str = names.CLOSE
) -> DataFrame:
    """
    Calculates the rolling standard deviation of a specified column in a Polars DataFrame
    and uses it to calculate lower and upper bands. The lower band is calculated as the
    input column values minus the standard deviation, while the upper band is calculated as
    the input column values plus the standard deviation.

    Args:
        dataframe: A Polars DataFrame containing numerical ("OHLC") data.
        window_size: An integer representing the size of the rolling window. Defaults to 10.
        column_name: A string representing the name of the column to calculate the rolling mean absolute
                     deviation on. Defaults to 'Close'.

    Returns:
        A Polars DataFrame with two additional columns containing the lower and upper bands for
        the specified input column, calculated as described above. The new columns are named using
        the ``names.sd_lower`` and ``names.sd_upper`` functions, which take the base column name and
        window size as arguments. If no valid numerical data can be found in the specified column,
        the new columns will contain null values.
    """
    dataframe_with_sd = standard_deviation(
        dataframe=dataframe, window_size=window_size, column_name=column_name
    )
    sd_column = names.sd(base_column=column_name, window_size=window_size)
    return dataframe_with_sd.with_columns(
        (col(column_name) - col(sd_column)).alias(
            names.sd_lower(base_column=column_name, window_size=window_size)
        ),
        (col(column_name) + col(sd_column)).alias(
            names.sd_upper(base_column=column_name, window_size=window_size)
        ),
    )


def average_absolute_deviation_bands(
    dataframe: DataFrame, window_size: int = 10, column_name: str = names.CLOSE
):
    """
    Calculates the rolling mean absolute deviation of a
    specified column in a Polars DataFrame and uses it to calculate lower and upper bands.
    The lower band is calculated as the input column values minus the mean absolute
    deviation, while the upper band is calculated as the input column values plus the mean
    absolute deviation.


    Args:
        dataframe: A Polars DataFrame containing numerical ("OHLC") data.
        window_size: An integer representing the size of the rolling window. Defaults to 10.
        column_name: A string representing the name of the column to calculate the rolling mean absolute
                     deviation on. Defaults to 'Close'.

    Returns:
        A Polars DataFrame with two additional columns containing the lower and upper bands for
        the specified input column, calculated as described above. The
        new columns are named using the ``names.aad_lower`` and ``names.aad_upper`` functions,
        which take the base column name and window size as arguments. If no valid numerical
        data can be found in the specified column, the new columns will contain null values.
    """
    dataframe_with_sd = average_absolute_deviation(
        dataframe=dataframe, window_size=window_size, column_name=column_name
    )
    aad_col = names.aad(base_column=column_name, window_size=window_size)
    return dataframe_with_sd.with_columns(
        (col(column_name) - col(aad_col)).alias(
            names.aad_lower(base_column=column_name, window_size=window_size)
        ),
        (col(column_name) + col(aad_col)).alias(
            names.aad_upper(base_column=column_name, window_size=window_size)
        ),
    )
