from bot.historical_data import load_historical_csv
from bot.backtest_strategy import (
    run_realistic_backtest,
    BacktestConfig,
)


PATH = "data/eurusd/eurusd_h1_2025.csv.csv"

DEVELOPMENT_SIZE = 1500
OOS_SIZE = 500
STEP = 500


def run_window(candles, start):
    dev_start = start
    dev_end = start + DEVELOPMENT_SIZE

    oos_start = dev_end
    oos_end = oos_start + OOS_SIZE

    if oos_end > len(candles):
        return None

    development = candles[dev_start:dev_end]
    oos = candles[oos_start:oos_end]

    config = BacktestConfig(
        starting_balance=1000.0,
        risk_percent=0.5,
        spread_pips=1.0,
        slippage_pips=0.2,
        commission_per_lot=7.0,
        pip_size=0.0001,
    )

    dev = run_realistic_backtest(
        development,
        config,
    )

    oos_result = run_realistic_backtest(
        oos,
        config,
    )

    return dev, oos_result


def main():
    candles = load_historical_csv(PATH)

    print("=== HMB FOREX AI V301 WALK-FORWARD ===")
    print(f"Total candles : {len(candles)}")
    print(
        f"Development   : {DEVELOPMENT_SIZE}"
    )
    print(f"OOS           : {OOS_SIZE}")
    print(f"Step          : {STEP}")

    results = []

    window = 1
    start = 0

    while True:
        result = run_window(
            candles,
            start,
        )

        if result is None:
            break

        dev, oos = result

        results.append(oos)

        print(f"\n=== WINDOW {window} ===")

        print(
            f"DEV | "
            f"trades={dev['total_trades']} "
            f"win={dev['win_rate']:.2f}% "
            f"net={dev['net_profit']:.2f} "
            f"PF={dev['profit_factor']:.2f}"
        )

        print(
            f"OOS | "
            f"trades={oos['total_trades']} "
            f"win={oos['win_rate']:.2f}% "
            f"net={oos['net_profit']:.2f} "
            f"PF={oos['profit_factor']:.2f}"
        )

        start += STEP
        window += 1

    if not results:
        print("\nNo complete windows available.")
        return

    total_oos_profit = sum(
        r["net_profit"]
        for r in results
    )

    profitable_windows = sum(
        r["net_profit"] > 0
        for r in results
    )

    valid_pf = [
        r["profit_factor"]
        for r in results
        if r["profit_factor"] != float("inf")
    ]

    average_pf = (
        sum(valid_pf) / len(valid_pf)
        if valid_pf
        else float("inf")
    )

    print("\n=== WALK-FORWARD SUMMARY ===")
    print(
        f"Windows             : {len(results)}"
    )
    print(
        f"Profitable OOS       : "
        f"{profitable_windows}/{len(results)}"
    )
    print(
        f"Total OOS net profit : "
        f"{total_oos_profit:.2f}"
    )
    print(
        f"Average OOS PF       : "
        f"{average_pf:.2f}"
    )


if __name__ == "__main__":
    main()
