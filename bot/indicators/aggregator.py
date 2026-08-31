import numpy as np

from .ema import ema
from .rsi import rsi
from .macd import macd
from .atr import atr


def analyze_market_series(high, low, close):
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)

    if not (len(high) == len(low) == len(close)):
        raise ValueError("high, low and close must have the same length")
    if len(close) < 50:
        raise ValueError("at least 50 candles are required")
    if not np.all(np.isfinite(high)) or not np.all(np.isfinite(low)) or not np.all(np.isfinite(close)):
        raise ValueError("OHLC arrays must contain only finite values")

    ema20 = ema(close, 20)
    ema50 = ema(close, 50)
    rsi14 = rsi(close, 14)
    macd_line, signal_line, histogram = macd(close)
    atr14 = atr(high, low, close, 14)

    trend = np.where(ema20 > ema50, "bullish", np.where(ema20 < ema50, "bearish", "neutral"))

    return {
        "price": close,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi14,
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_histogram": histogram,
        "atr": atr14,
        "trend": trend,
    }


def analyze_market(high, low, close):
    series = analyze_market_series(high, low, close)
    i = len(close) - 1
    return {
        "price": float(series["price"][i]),
        "ema20": float(series["ema20"][i]),
        "ema50": float(series["ema50"][i]),
        "rsi": float(series["rsi"][i]),
        "macd": float(series["macd"][i]),
        "macd_signal": float(series["macd_signal"][i]),
        "macd_histogram": float(series["macd_histogram"][i]),
        "atr": float(series["atr"][i]),
        "trend": str(series["trend"][i]),
    }
