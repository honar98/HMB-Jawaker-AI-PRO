import numpy as np


def rsi(values, period=14):
    values = np.asarray(values, dtype=float)

    if period <= 0:
        raise ValueError("period must be greater than 0")

    if len(values) <= period:
        raise ValueError("not enough values for RSI")

    delta = np.diff(values)

    gains = np.maximum(delta, 0.0)
    losses = np.maximum(-delta, 0.0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    result = np.full(len(values), np.nan, dtype=float)

    if avg_loss == 0:
        result[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[period] = 100.0 - (100.0 / (1.0 + rs))

    for i in range(period + 1, len(values)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i - 1]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i - 1]) / period

        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100.0 - (100.0 / (1.0 + rs))

    return result
