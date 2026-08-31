import numpy as np

from .ema import ema


def macd(values, fast_period=12, slow_period=26, signal_period=9):
    values = np.asarray(values, dtype=float)

    if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
        raise ValueError("periods must be greater than 0")

    if fast_period >= slow_period:
        raise ValueError("fast_period must be smaller than slow_period")

    if len(values) < slow_period + signal_period - 1:
        raise ValueError("not enough values for MACD")

    fast_ema = ema(values, fast_period)
    slow_ema = ema(values, slow_period)

    line = fast_ema - slow_ema

    valid_line = line[slow_period - 1:]
    signal_valid = ema(valid_line, signal_period)

    signal_line = np.full(len(values), np.nan, dtype=float)
    start = slow_period + signal_period - 2
    signal_line[start:] = signal_valid[signal_period - 1:]

    histogram = line - signal_line

    return line, signal_line, histogram
