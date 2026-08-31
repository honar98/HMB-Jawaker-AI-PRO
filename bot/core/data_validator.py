from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    total_candles: int
    duplicate_timestamps: int
    missing_intervals: int
    market_closed_intervals: int
    unexpected_missing_intervals: int
    invalid_ohlc: int
    invalid_prices: int
    invalid_volume: int
    errors: tuple[str, ...]


def _is_weekend(timestamp):
    return timestamp.weekday() >= 5


def _is_expected_market_closure(timestamp):
    """Return True for normal EURUSD weekly/holiday data gaps.

    The supplied broker-style H1 data closes late Friday. The UTC close hour
    changes with DST, so Friday 20:00+ or 21:00+ gaps are expected rather than
    being treated as missing market data. Weekends and Christmas are also
    expected closures for this 2025 dataset.
    """
    if _is_weekend(timestamp):
        return True

    if timestamp.weekday() == 4 and timestamp.hour >= 20:
        return True

    if timestamp.date().isoformat() == "2025-12-25":
        return True

    return False


def validate_candles(candles, timeframe_minutes=60):
    errors = []

    duplicate_timestamps = 0
    missing_intervals = 0
    market_closed_intervals = 0
    unexpected_missing_intervals = 0
    invalid_ohlc = 0
    invalid_prices = 0
    invalid_volume = 0

    if not candles:
        return ValidationReport(
            False, 0, 0, 0, 0, 0, 0, 0, 0,
            ("No candles supplied",),
        )

    seen = set()

    for i, candle in enumerate(candles):
        required = (
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
        )

        missing_fields = [
            field for field in required
            if field not in candle
        ]

        if missing_fields:
            errors.append(
                f"Missing fields at index {i}: "
                f"{', '.join(missing_fields)}"
            )
            continue

        timestamp = candle["time"]

        if timestamp in seen:
            duplicate_timestamps += 1

        seen.add(timestamp)

        try:
            o = float(candle["open"])
            h = float(candle["high"])
            l = float(candle["low"])
            c = float(candle["close"])
            v = float(candle["volume"])

            if min(o, h, l, c) <= 0:
                invalid_prices += 1

            if h < max(o, c) or l > min(o, c) or h < l:
                invalid_ohlc += 1

            if v < 0:
                invalid_volume += 1

        except (TypeError, ValueError):
            invalid_prices += 1

        if i > 0:
            previous = candles[i - 1]["time"]
            expected = previous + timedelta(minutes=timeframe_minutes)

            if timestamp < previous:
                errors.append(
                    f"Timestamp out of order at index {i}"
                )

            elif timestamp > expected:
                current = expected

                while current < timestamp:
                    missing_intervals += 1

                    if _is_expected_market_closure(current):
                        market_closed_intervals += 1
                    else:
                        unexpected_missing_intervals += 1

                    current += timedelta(minutes=timeframe_minutes)

    if duplicate_timestamps:
        errors.append(
            f"Duplicate timestamps: {duplicate_timestamps}"
        )

    if unexpected_missing_intervals:
        errors.append(
            "Unexpected missing intervals: "
            f"{unexpected_missing_intervals}"
        )

    if invalid_ohlc:
        errors.append(
            f"Invalid OHLC candles: {invalid_ohlc}"
        )

    if invalid_prices:
        errors.append(
            f"Invalid prices: {invalid_prices}"
        )

    if invalid_volume:
        errors.append(
            f"Invalid volumes: {invalid_volume}"
        )

    valid = not errors

    return ValidationReport(
        valid=valid,
        total_candles=len(candles),
        duplicate_timestamps=duplicate_timestamps,
        missing_intervals=missing_intervals,
        market_closed_intervals=market_closed_intervals,
        unexpected_missing_intervals=unexpected_missing_intervals,
        invalid_ohlc=invalid_ohlc,
        invalid_prices=invalid_prices,
        invalid_volume=invalid_volume,
        errors=tuple(errors),
    )
