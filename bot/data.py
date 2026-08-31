import csv
from pathlib import Path


REQUIRED_COLUMNS = {"time", "open", "high", "low", "close", "volume"}


def load_candles(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV has no header")

        columns = {column.strip().lower() for column in reader.fieldnames}

        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"Missing columns: {', '.join(sorted(missing))}"
            )

        candles = []

        for row in reader:
            candles.append({
                "time": row["time"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            })

    if not candles:
        raise ValueError("CSV contains no candles")

    return candles
