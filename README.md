# HMB FOREX AI V301

A research/backtesting project for EURUSD H1. **Live trading is disabled by default.**

## Safety and realism
- No look-ahead from future candles.
- A signal is generated only after a candle closes and is entered on the next candle's open, with spread/slippage applied.
- Each OHLC candle is processed exactly once.
- Same-candle SL/TP collisions use a conservative stop-first rule.
- Gap-through SL/TP is filled at the candle open rather than the stale order price.
- Position sizing is based on account risk, stop distance, pip value, lot step and margin checks.
- Commission is included in net P&L.
- Daily loss baseline resets on each UTC trading day.
- Drawdown tracks mark-to-market equity through the execution engine.
- Walk-forward and out-of-sample scripts are provided to reduce overfitting risk.

## Commands

```bash
python -m bot.validate_data data/eurusd/eurusd_h1_2025.csv.csv
python -m bot.run_backtest data/eurusd/eurusd_h1_2025.csv.csv
python -m bot.run_performance data/eurusd/eurusd_h1_2025.csv.csv
python -m bot.oos_backtest
python -m bot.walk_forward
python -m unittest discover -s tests -v
```

This project is for research only. Backtest performance does not guarantee live profitability.
