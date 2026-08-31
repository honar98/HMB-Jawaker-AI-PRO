import numpy as np


def ema(values, period):
    values = np.asarray(values, dtype=float)

    if period <= 0:
        raise ValueError("period must be greater than 0")

    if len(values) < period:
        raise ValueError("not enough values for EMA")

    result = np.empty(len(values), dtype=float)
    result[:period - 1] = np.nan
    result[period - 1] = np.mean(values[:period])

    alpha = 2.0 / (period + 1.0)

    for i in range(period, len(values)):
        result[i] = alpha * values[i] + (1.0 - alpha) * result[i - 1]

    return result
