import sys

from bot.historical_data import load_historical_csv
from bot.backtest_strategy import run_realistic_backtest, BacktestConfig


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m bot.run_backtest <csv_file>")
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

    print("\n=== HMB FOREX AI V301 BACKTEST ===")
    print(f"Starting balance : {result['starting_balance']:.2f}")
    print(f"Ending balance   : {result['ending_balance']:.2f}")
    print(f"Total trades     : {result['total_trades']}")
    print(f"Wins             : {result['wins']}")
    print(f"Losses           : {result['losses']}")
    print(f"Win rate         : {result['win_rate']:.2f}%")
    print(f"Net profit       : {result['net_profit']:.2f}")
    print(f"Max drawdown     : {result['max_drawdown']:.2f}")
    print(f"Profit factor    : {result['profit_factor']:.2f}")
    print(f"Commission       : {result['total_commission']:.2f}")


if __name__ == "__main__":
    main()
