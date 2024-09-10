import indicatory.names as names

from polars import DataFrame, col, when, cum_sum


PREV_CLOSE_COL = "Previous Close"
OBV_DIFF_COL = "OBV Diff"


def on_balance_volume(dataframe: DataFrame) -> DataFrame:
    """
    Calculates the On-Balance-Volume (OBV) over the volume for a given dataframe of financial data ("OHLCV").

    Args:
        dataframe: The input dataframe with financial data. It should contain at least a column "Volume" which
                   represents the volume of the asset.

    Returns:
        DataFrame with added column "OBV" representing the on-balance-volume.
    """
    close_volume = dataframe.select(
        col(names.DATE, names.CLOSE, names.VOLUME)
    ).with_columns(col(names.CLOSE).shift(1).alias(PREV_CLOSE_COL))
    close_volume_factors = close_volume.with_columns(
        when(col(names.CLOSE) > col(PREV_CLOSE_COL))
        .then(col(names.VOLUME))
        .when(col(names.CLOSE) < col(PREV_CLOSE_COL))
        .then(-1 * col(names.VOLUME))
        .otherwise(0)
        .alias(OBV_DIFF_COL)
    )
    close_volume_obv = close_volume_factors.with_columns(
        cum_sum(OBV_DIFF_COL).alias(names.obv())
    )
    return dataframe.with_columns(
        close_volume_obv.select(col(names.obv())).to_series().alias(names.obv())
    )


def price_by_volume(dataframe: DataFrame, price_column: str = names.CLOSE):
    """
    Calculates the Price-by-Volume (PV) for a given dataframe of financial data ("OHLCV").

    The "price-by-volume" is simply the price (open, high, low, close or 'average') of an asset
    divided by its current volume.

    Args:
        dataframe: The input dataframe with financial data ("OHLCV"). It should contain at least one
                   column with price data and a column "Volume" representing the volume of the asset.
        price_column: Name of the price column to be used here.

    Returns:
        DataFrame with a new column representing the on-balance-volume. The name of the column can
        be determined using ``indicatory.names.pv('price_column')``.
    """
    return dataframe.with_columns(
        (col.Volume / col(price_column)).alias(names.pv(price_column))
    )
