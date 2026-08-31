import sys

from bot.historical_data import load_historical_csv
from bot.core.data_validator import validate_candles


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m bot.validate_data <csv_file>")
        raise SystemExit(1)

    candles = load_historical_csv(sys.argv[1])
    report = validate_candles(candles)

    print("=== HMB FOREX AI DATA VALIDATION ===")
    print(f"Candles                  : {report.total_candles}")
    print(f"Duplicate timestamps     : {report.duplicate_timestamps}")
    print(f"Missing intervals        : {report.missing_intervals}")
    print(f"Expected market closure  : {report.market_closed_intervals}")
    print(f"Unexpected missing       : {report.unexpected_missing_intervals}")
    print(f"Invalid OHLC              : {report.invalid_ohlc}")
    print(f"Invalid prices            : {report.invalid_prices}")
    print(f"Invalid volume            : {report.invalid_volume}")
    print(f"VALID                     : {'YES' if report.valid else 'NO'}")

    for error in report.errors:
        print(f"ERROR: {error}")

    raise SystemExit(0 if report.valid else 2)


if __name__ == "__main__":
    main()
