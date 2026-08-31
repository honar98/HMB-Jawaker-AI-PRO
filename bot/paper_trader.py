from bot.historical_data import load_historical_csv
from bot.backtest_strategy import run_realistic_backtest, BacktestConfig


CSV = "data/eurusd/eurusd_h1_2025.csv.csv"

cfg = BacktestConfig(
    starting_balance=1000.0,
    risk_percent=0.5,
    spread_pips=1.0,
    slippage_pips=0.2,
    commission_per_lot=7.0,
    pip_size=0.0001,
)

print("======================================")
print(" HMB FOREX AI V302 PAPER TRADER")
print("======================================")
print("MODE        : PAPER ONLY")
print("LIVE ORDERS : DISABLED")
print("SIDE        : BUY ONLY")
print("RISK        : 0.5%")
print("--------------------------------------")

candles = load_historical_csv(CSV)

result = run_realistic_backtest(candles, cfg)

# V302: BUY only
trades = [
    t for t in result["trades"]
    if t["side"] == "BUY"
]

wins = sum(t["profit"] > 0 for t in trades)
losses = sum(t["profit"] < 0 for t in trades)

gross_profit = sum(
    t["profit"] for t in trades
    if t["profit"] > 0
)

gross_loss = abs(sum(
    t["profit"] for t in trades
    if t["profit"] < 0
))

net = sum(t["profit"] for t in trades)
pf = gross_profit / gross_loss if gross_loss else float("inf")

commission = sum(
    t.get("commission", 0)
    for t in trades
)

print(f"Total candles : {len(candles)}")
print(f"BUY trades    : {len(trades)}")
print(f"Wins          : {wins}")
print(f"Losses        : {losses}")

if trades:
    print(f"Win rate      : {wins / len(trades) * 100:.2f}%")
else:
    print("Win rate      : 0.00%")

print(f"Net P&L       : {net:.2f}")
print(f"Profit Factor : {pf:.2f}")
print(f"Commission    : {commission:.2f}")

print("--------------------------------------")
print("PAPER TEST COMPLETE")
print("NO REAL ORDERS WERE SENT.")
print("======================================")
