import csv
from pathlib import Path
from datetime import datetime, timezone


REQUIRED_COLUMNS = {
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
}


def load_historical_csv(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    candles = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV has no header")

        columns = {
            column.strip().lower()
            for column in reader.fieldnames
        }

        missing = REQUIRED_COLUMNS - columns

        if missing:
            raise ValueError(
                f"Missing columns: {', '.join(sorted(missing))}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                timestamp_ms = int(float(row["timestamp"]))

                candle = {
                    "time": datetime.fromtimestamp(
                        timestamp_ms / 1000,
                        tz=timezone.utc,
                    ),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                }

                if candle["high"] < candle["low"]:
                    raise ValueError("high is lower than low")

                if candle["open"] <= 0 or candle["close"] <= 0:
                    raise ValueError("price must be greater than zero")

                if candle["low"] <= 0:
                    raise ValueError("low must be greater than zero")

                candles.append(candle)

            except (ValueError, TypeError, OverflowError) as exc:
                raise ValueError(
                    f"Invalid candle at CSV row {row_number}: {exc}"
                ) from exc

    if not candles:
        raise ValueError("CSV contains no candles")

    candles.sort(key=lambda candle: candle["time"])

    return candles
