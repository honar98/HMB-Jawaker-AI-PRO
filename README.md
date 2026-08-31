# 📈 HMB FOREX AI V302

Professional EURUSD H1 research, backtesting and paper-trading system.

## 🚀 Current Version

**V302 — BUY ONLY**

- 🟢 BUY signals enabled
- 🔴 SELL signals disabled
- 🧪 Paper Trading enabled
- 🚫 Real Orders disabled
- 🚫 MT5 Live Trading disabled
- 💰 Risk per trade: 0.5%

## 🧠 BUY Strategy

A BUY signal requires:

- Bullish EMA trend
- RSI between 60–68
- MACD bullish confirmation
- MACD histogram > 0
- Score >= 85

## 🛡️ Risk Protection

The execution engine includes:

- Account-risk position sizing
- Stop-loss validation
- Minimum / maximum lot protection
- Daily loss protection
- Maximum drawdown protection
- Margin checks
- Spread and slippage simulation
- Commission accounting
- Gap-aware SL/TP execution
- Conservative same-candle SL/TP handling

## 📊 V302 Walk-Forward Results

Test configuration:

- Development: 1500 candles
- Out-of-sample: 500 candles
- Step: 500 candles
- Windows: 9

Results:

- Profitable OOS windows: **7/9**
- Total OOS net profit: **+80.41**
- Average OOS Profit Factor: **1.66**

These are historical research results and do not guarantee future profitability.

## 🧪 Safety Tests

Run:

```bash
PYTHONPATH="$PWD" python tests/test_safety.py
PYTHONPATH="$PWD" python -m unittest discover -s tests -v
