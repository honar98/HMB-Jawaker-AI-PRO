import sys

from bot.historical_data import load_historical_csv
from bot.backtest_strategy import run_realistic_backtest, BacktestConfig
from bot.performance import analyze_performance


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m bot.run_performance <csv_file>")
        raise SystemExit(1)

    candles = load_historical_csv(sys.argv[1])

    config = BacktestConfig(
        starting_balance=1000.0,
        risk_percent=0.5,
        spread_pips=1.0,
        slippage_pips=0.2,
        commission_per_lot=7.0,
        pip_size=0.0001,
    )

    result = run_realistic_backtest(candles, config)
    report = analyze_performance(result["trades"])

    print("\n=== HMB FOREX AI V301 PERFORMANCE ===")
    print(f"Total trades          : {report['total_trades']}")
    print(f"BUY trades            : {report['buy_trades']}")
    print(f"SELL trades           : {report['sell_trades']}")
    print(f"Wins                  : {report['wins']}")
    print(f"Losses                : {report['losses']}")
    print(f"Net profit            : {report['net_profit']:.2f}")
    print(f"Average win           : {report['average_win']:.4f}")
    print(f"Average loss          : {report['average_loss']:.4f}")
    print(f"Max consecutive loss  : {report['max_consecutive_losses']}")

    print("\n--- BY SIDE ---")
    for side, data in report["by_side"].items():
        print(
            f"{side}: trades={data['trades']} "
            f"wins={data['wins']} "
            f"losses={data['losses']} "
            f"win_rate={data['win_rate']:.2f}% "
            f"net={data['net_profit']:.2f} "
            f"PF={data['profit_factor']:.2f}"
        )

    print("\n--- EXIT REASONS ---")
    for reason, count in report["exit_reasons"].items():
        print(f"{reason}: {count}")

    print("\n--- MONTHLY ---")
    for month, data in report["by_month"].items():
        print(
            f"{month}: trades={data['trades']} "
            f"win_rate={data['win_rate']:.2f}% "
            f"net={data['net_profit']:.2f} "
            f"PF={data['profit_factor']:.2f}"
        )


if __name__ == "__main__":
    main()
