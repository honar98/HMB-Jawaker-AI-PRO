import numpy as np


def atr(high, low, close, period=14):
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)

    if period <= 0:
        raise ValueError("period must be greater than 0")

    if not (len(high) == len(low) == len(close)):
        raise ValueError("high, low and close must have the same length")

    if len(close) <= period:
        raise ValueError("not enough values for ATR")

    true_range = np.empty(len(close), dtype=float)

    true_range[0] = high[0] - low[0]

    for i in range(1, len(close)):
        true_range[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1]),
        )

    result = np.full(len(close), np.nan, dtype=float)

    result[period] = np.mean(true_range[:period + 1])

    for i in range(period + 1, len(close)):
        result[i] = (
            (result[i - 1] * (period - 1)) + true_range[i]
        ) / period

    return result
