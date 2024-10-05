# OHLC(V) column names used throughout `indicatory`. Constants since they do not change.
DATE = "Date"
OPEN = "Open"
HIGH = "High"
LOW = "Low"
CLOSE = "Close"
VOLUME = "Volume"


def avg_price() -> str:
    """
    Returns:
        Name of the column containing the calculated average price data.
    """
    return "AVG Price"


def _heikin_ashi(suffix: str) -> str:
    return f"HA {suffix}"


def ha_open() -> str:
    """
    Returns:
        Name of the column containing the calculated Heikin Ashi opening price data.
    """
    return _heikin_ashi(OPEN)


def ha_high() -> str:
    """
    Returns:
        Name of the column containing the calculated Heikin Ashi price data for "daily high".
    """
    return _heikin_ashi(HIGH)


def ha_low() -> str:
    """
    Returns:
        Name of the column containing the calculated Heikin Ashi price data for "daily low".
    """
    return _heikin_ashi(LOW)


def ha_close() -> str:
    """
    Returns:
        Name of the column containing the calculated Heikin Ashi closing price data.
    """
    return _heikin_ashi(CLOSE)


def rcs_open() -> str:
    """
    Returns:
        Name of the column containing the calculated Relative Currency Strength (RCS) opening price data.
    """
    return "RSC Open"


def rcs_close() -> str:
    """
    Returns:
        Name of the column containing the calculated Relative Currency Strength (RCS) closing price data.
    """
    return "RCS Close"


def roc(column: str) -> str:
    return f"roc {column}"


def _with_window_size(name: str, window_size: int) -> str:
    return f"{name} {window_size}"


def _with_column_and_window_size(name: str, column: str, window_size: int) -> str:
    return f"{_with_window_size(name=name, window_size=window_size)} {column}"


def sd(base_column: str, window_size: int) -> str:
    """
    Args:
        base_column: Name of the column used to calculate the standard deviation values.
        window_size: The number of periods to use for calculating standard deviation.

    Returns:
        Name of the column containing the calculated standard deviation values.
    """
    return _with_column_and_window_size(
        name="STD", column=base_column, window_size=window_size
    )


def sd_lower(base_column: str, window_size: int):
    """
    Args:
        base_column: Name of the column used to calculate the standard deviation values.
        window_size: The number of periods to use for calculating standard deviation.

    Returns:
        Name of the column containing the calculated standard deviation values for the *lower* SD band.
    """
    return _with_column_and_window_size(
        "SD (low)", column=base_column, window_size=window_size
    )


def sd_upper(base_column: str, window_size: int):
    """
    Args:
        base_column: Name of the column used to calculate the standard deviation values.
        window_size: The number of periods to use for calculating standard deviation.

    Returns:
        Name of the column containing the calculated standard deviation values for the *upper* SD band.
    """
    return _with_column_and_window_size(
        "SD (up)", column=base_column, window_size=window_size
    )


def var(base_column: str, window_size: int) -> str:
    """
    Args:
        base_column: Name of the column used to calculate the variance values.
        window_size: The number of periods to use for calculating variance.

    Returns:
        Name of the column containing the calculated variance values.
    """
    return _with_column_and_window_size(
        name="VAR", column=base_column, window_size=window_size
    )


def aad(base_column: str, window_size: int) -> str:
    """
    Args:
        base_column: Name of the column used to calculate the average absolute deviation values.
        window_size: The number of periods to use for calculating average absolute deviation values.

    Returns:
        Name of the column containing the calculated average absolute deviation (AAD) values.
    """
    return _with_column_and_window_size(
        name="AAD", column=base_column, window_size=window_size
    )


def aad_lower(base_column: str, window_size: int) -> str:
    """
    Args:
        base_column: Name of the column used to calculate the average absolute deviation values.
        window_size: The number of periods to use for calculating average absolute deviation values.

    Returns:
        Name of the column containing the calculated average absolute deviation values for the *lower* AAD band.
    """
    return _with_column_and_window_size(
        "AAD (low)", column=base_column, window_size=window_size
    )


def aad_upper(base_column: str, window_size: int) -> str:
    """
    Args:
        base_column: Name of the column used to calculate the average absolute deviation values.
        window_size: The number of periods to use for calculating average absolute deviation values.

    Returns:
        Name of the column containing the calculated average absolute deviation values for the *upper* AAD band.
    """
    return _with_column_and_window_size(
        "AAD (up)", column=base_column, window_size=window_size
    )


def sma(column_name: str, window_size: int) -> str:
    """
    Args:
        column_name: Name of the column used to calculate the simple moving average values.
        window_size: The number of periods to use for calculating simple moving average values.

    Returns:
        Name of the column containing the calculated simple moving average (SMA) values.
    """
    return _with_column_and_window_size(
        "SMA", column=column_name, window_size=window_size
    )


def ema(column_name: str, window_size: int) -> str:
    """
    Args:
        column_name: Name of the column used to calculate the exponential moving average values.
        window_size: The number of periods to use for calculating exponential moving average values.

    Returns:
        Name of the column containing the calculated exponential moving average (EMA) values.
    """
    return _with_column_and_window_size(
        "EMA", column=column_name, window_size=window_size
    )


def macd(short_window: int, long_window: int) -> str:
    """
    Args:
        short_window: The number of periods to use for calculating the *short* SMA values.
        long_window: The number of periods to use for calculating the *long* SMA values.

    Returns:
        Name of the column containing the calculated Moving Average Convergence / Divergence (MACD) values.
    """
    return f"MACD {short_window}/{long_window}"


def macd_sig(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating the MACD signal.

    Returns:
        Name of the column containing the calculated Moving Average Convergence / Divergence (MACD) signal values.
    """
    return _with_window_size("SIG", window_size=window_size)


def mm(column_name: str, window_size: int) -> str:
    """
    Args:
        column_name: Name of the column used to calculate the moving median values.
        window_size: The number of periods to use for calculating moving median values.

    Returns:
        Name of the column containing the calculated Moving Median (MM) values.
    """
    return _with_column_and_window_size(
        "MM", column=column_name, window_size=window_size
    )


def ppo(column_name: str, short_window_size: int, long_window_size: int) -> str:
    """
    Args:
        column_name: Name of the column used to calculate the percentage price oscillation values.
        short_window_size: The number of periods to use for calculating the *short* SMA values.
        long_window_size: The number of periods to use for calculating the *long* SMA values.

    Returns:
        Name of the column containing the calculated Percentage Price Oscillator (PPO) values.
    """
    return f"PPO {short_window_size}/{long_window_size} {column_name}"


def rs(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating relative strength values.

    Returns:
        Name of the column containing the calculated Relative Strength (RS) values.
    """
    return _with_window_size("RS", window_size=window_size)


def rsi(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating relative strength index values.

    Returns:
        Name of the column containing the calculated Relative Strength Index (RSI) values
        (both simple and "classic")
    """
    return _with_window_size("RSI", window_size=window_size)


def fast_k(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating stochastic oscillation values.

    Returns:
        Name of the column containing calculated Stochastic Oscillator (SO) values for the "Fast K%" part.
    """
    return _with_window_size("Fast %K", window_size=window_size)


def fast_d(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating stochastic oscillation values.

    Returns:
        Name of the column containing calculated Stochastic Oscillator (SO) values for the "Fast D%" part.
    """
    return _with_window_size("Fast %D", window_size=window_size)


def slow_k(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating stochastic oscillation values.

    Returns:
        Name of the column containing calculated Stochastic Oscillator (SO) values for the "Slow K%" part.
    """
    return _with_window_size("Slow %K", window_size=window_size)


def slow_d(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating stochastic oscillation values.

    Returns:
        Name of the column containing calculated Stochastic Oscillator (SO) values for the "Slow D%" part.
    """
    return _with_window_size("Slow %D", window_size=window_size)


def dret() -> str:
    """
    Returns:
        Name of the column containing the calculated Daily Returns.
    """
    return "Daily Returns"


def dret_pct() -> str:
    """
    Returns:
        Name of the column containing the calculated Daily Returns (in percent).
    """
    return dret() + " (%)"


def dran() -> str:
    """
    Returns:
        Name of the column containing the calculated Daily Range values.
    """
    return "Daily Range"


def dran_pct() -> str:
    """
    Returns:
        Name of the column containing the calculated Daily Range values (in percent).
    """
    return dran() + " (%)"


def tr() -> str:
    """
    Returns:
        Name of the column containing the calculated True Range values.
    """
    return "TR"


def atr(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating the average true range.

    Returns:
        Name of the column containing the calculated Average True Range (ATR).
    """
    return _with_window_size("ATR", window_size=window_size)


def atr_pct(window_size: int) -> str:
    """
    Args:
        window_size: The number of periods to use for calculating the average true range.

    Returns:
        Name of the column containing the calculated Average True Range (ATR, in percent).
    """
    return atr(window_size=window_size) + " (%)"


def obv() -> str:
    """
    Returns:
        Name of the column containing the calculated On-Balance Volume (OBV).
    """
    return "OBV"


def pv(column_name: str) -> str:
    """
    Args:
        column_name: Name of the column used to calculate "price-by-volume".

    Returns:
        Name of the column containing the calculated Price-by-Volume (PV) values.
    """
    return f"PV {column_name}"


def dpo(column_name: str, window_size: int) -> str:
    return _with_column_and_window_size(
        "DPO", column=column_name, window_size=window_size
    )
