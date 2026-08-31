from datetime import datetime, timezone

from bot.historical_data import load_historical_csv
from bot.backtest_strategy import run_realistic_backtest, BacktestConfig


def split_data(candles):
    cutoff = datetime(2025, 10, 1, tzinfo=timezone.utc)

    development = [
        c for c in candles
        if c["time"] < cutoff
    ]

    out_of_sample = [
        c for c in candles
        if c["time"] >= cutoff
    ]

    return development, out_of_sample


def main():
    path = "data/eurusd/eurusd_h1_2025.csv.csv"

    candles = load_historical_csv(path)
    development, oos = split_data(candles)

    print("=== HMB FOREX AI V301 DATA SPLIT ===")
    print(f"Total candles       : {len(candles)}")
    print(f"Development candles : {len(development)}")
    print(f"OOS candles         : {len(oos)}")

    config = BacktestConfig(
        starting_balance=1000.0,
        risk_percent=0.5,
        spread_pips=1.0,
        slippage_pips=0.2,
        commission_per_lot=7.0,
        pip_size=0.0001,
    )

    if len(development) >= 60:
        dev_result = run_realistic_backtest(
            development,
            config,
        )

        print("\n=== DEVELOPMENT RESULT ===")
        print(f"Trades        : {dev_result['total_trades']}")
        print(f"Win rate      : {dev_result['win_rate']:.2f}%")
        print(f"Net profit    : {dev_result['net_profit']:.2f}")
        print(f"Max drawdown  : {dev_result['max_drawdown']:.2f}")
        print(f"Profit factor : {dev_result['profit_factor']:.2f}")
        print(f"Commission    : {dev_result['total_commission']:.2f}")

    if len(oos) >= 60:
        oos_result = run_realistic_backtest(
            oos,
            config,
        )

        print("\n=== OUT-OF-SAMPLE RESULT ===")
        print(f"Trades        : {oos_result['total_trades']}")
        print(f"Win rate      : {oos_result['win_rate']:.2f}%")
        print(f"Net profit    : {oos_result['net_profit']:.2f}")
        print(f"Max drawdown  : {oos_result['max_drawdown']:.2f}")
        print(f"Profit factor : {oos_result['profit_factor']:.2f}")
        print(f"Commission    : {oos_result['total_commission']:.2f}")


if __name__ == "__main__":
    main()
