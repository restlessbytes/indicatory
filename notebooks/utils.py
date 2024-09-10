import polars
import hvplot.polars
import holoviews as hv

from polars import DataFrame

HEIGHT = 600
WIDTH = 1200


def load_asset_data(symbol: str) -> DataFrame:
    return polars.read_csv(f"../tests/data/{symbol.upper()}.csv", try_parse_dates=True)


def ohlc_plot(dataframe: DataFrame):
    return dataframe.hvplot.ohlc(
        x="Date",
        y=["Open", "High", "Low", "Close"],
        grid=True,
        height=HEIGHT,
        width=WIDTH,
    )


def bar_plot(
    dataframe: DataFrame,
    value_field: str,
    is_small: bool = True,
    color: str = "lightblue",
):
    height = int(HEIGHT / 3) if is_small else HEIGHT
    return dataframe.hvplot.bar(
        x="Date", y=value_field, grid=True, height=height, width=WIDTH, color=color
    )


def scatter_plot(
    dataframe: DataFrame,
    value_fields: list[str],
    is_small: bool = True,
    color: str | list[str] = "purple",
):
    height = int(HEIGHT / 3) if is_small else HEIGHT
    return dataframe.hvplot.scatter(
        x="Date", y=value_fields, color=color, grid=True, width=WIDTH, height=height
    )


def lines_plot(
    dataframe: DataFrame,
    value_fields: list[str],
    is_small: bool = True,
    color: str | list[str] = "lightblue",
):
    height = int(HEIGHT / 3) if is_small else HEIGHT
    return dataframe.hvplot.line(
        x="Date", y=value_fields, color=color, grid=True, width=WIDTH, height=height
    )
