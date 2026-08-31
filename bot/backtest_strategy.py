from dataclasses import dataclass

from bot.strategy.engine import _signal_from_market
from bot.indicators.aggregator import analyze_market_series
from bot.execution.account import Account
from bot.execution.costs import ExecutionCosts
from bot.execution.risk_engine import RiskConfig
from bot.execution.trade_engine import TradeEngine


@dataclass(frozen=True)
class BacktestConfig:
    starting_balance: float = 1000.0
    risk_percent: float = 0.5
    spread_pips: float = 1.0
    slippage_pips: float = 0.2
    commission_per_lot: float = 7.0
    pip_size: float = 0.0001
    max_daily_loss_percent: float = 2.0
    max_drawdown_percent: float = 10.0
    leverage: float = 100.0
    min_lot: float = 0.01
    max_lot: float = 5.0
    lot_step: float = 0.01


def _trade_record(candle, event, meta):
    return {
        "time": str(candle["time"]),
        "side": event.side,
        "entry": meta.get("entry"),
        "exit": event.exit_price,
        "stop": meta.get("stop"),
        "target": meta.get("target"),
        "position_size": meta.get("position_size"),
        "profit": event.net_pnl,
        "gross_profit": event.pnl,
        "commission": event.commission,
        "reason": event.reason,
        "score": meta.get("score"),
        "atr": meta.get("atr"),
        "trend": meta.get("trend"),
        "rsi": meta.get("rsi"),
        "macd": meta.get("macd"),
        "macd_signal": meta.get("macd_signal"),
    }


def run_realistic_backtest(candles, config=None):
    config = config or BacktestConfig()

    if len(candles) < 60:
        raise ValueError("At least 60 candles are required")

    account = Account(config.starting_balance)
    engine = TradeEngine(
        account=account,
        execution_costs=ExecutionCosts(
            spread_pips=config.spread_pips,
            slippage_pips=config.slippage_pips,
            commission_per_lot=config.commission_per_lot,
            pip_size=config.pip_size,
        ),
        risk_config=RiskConfig(
            risk_percent=config.risk_percent,
            max_daily_loss_percent=config.max_daily_loss_percent,
            max_drawdown_percent=config.max_drawdown_percent,
            pip_size=config.pip_size,
            leverage=config.leverage,
            min_lot=config.min_lot,
            max_lot=config.max_lot,
            lot_step=config.lot_step,
        ),
    )

    closes = [float(c["close"]) for c in candles]
    highs = [float(c["high"]) for c in candles]
    lows = [float(c["low"]) for c in candles]
    indicators = analyze_market_series(highs, lows, closes)
    trades = []
    open_meta = None

    for i, candle in enumerate(candles):

        # Reset the daily risk baseline at the first candle of each UTC day.
        engine.start_new_day(candle["time"])

        # A candle is processed exactly once. This is critical: a newly opened
        # position is NOT processed against the same candle twice.
        if engine.account.positions:
            result = engine.process_candle(
                candle["open"], candle["high"], candle["low"], candle["close"]
            )
            for event in result["events"]:
                trades.append(_trade_record(candle, event, open_meta or {}))
                open_meta = None
            continue

        if i < 49 or i >= len(candles) - 1:
            continue

        market = {
            "price": float(indicators["price"][i]),
            "ema20": float(indicators["ema20"][i]),
            "ema50": float(indicators["ema50"][i]),
            "rsi": float(indicators["rsi"][i]),
            "macd": float(indicators["macd"][i]),
            "macd_signal": float(indicators["macd_signal"][i]),
            "macd_histogram": float(indicators["macd_histogram"][i]),
            "atr": float(indicators["atr"][i]),
            "trend": str(indicators["trend"][i]),
        }
        signal = _signal_from_market(market)
        if signal["action"] not in ("BUY", "SELL"):
            continue

        next_candle = candles[i + 1]
        side = signal["action"]
        entry_reference = float(next_candle["open"])
        atr_value = float(signal["atr"])

        if side == "BUY":
            stop = entry_reference - atr_value * 1.5
            target = entry_reference + atr_value * 2.5
        else:
            stop = entry_reference + atr_value * 1.5
            target = entry_reference - atr_value * 2.5

        opened = engine.open_trade(side, entry_reference, stop, target)
        if not opened.opened:
            continue

        open_meta = {
            "entry": opened.entry,
            "stop": opened.stop_loss,
            "target": opened.take_profit,
            "position_size": opened.size,
            "score": signal["score"],
            "atr": signal["atr"],
            "trend": signal["trend"],
            "rsi": signal["rsi"],
            "macd": signal["macd"],
            "macd_signal": signal["macd_signal"],
        }

        # Deliberately do not process next_candle here. The next loop iteration
        # owns that candle, preventing double-counting and look-ahead-like bias.

    # Close any remaining position at the final executable market price.
    for position in list(account.positions):
        event = engine.close_trade(
            position,
            float(candles[-1]["close"]),
            reason="END_OF_DATA",
        )
        trades.append(_trade_record(candles[-1], event, open_meta or {
            "entry": position.entry,
            "stop": position.stop_loss,
            "target": position.take_profit,
            "position_size": position.size,
        }))
        open_meta = None

    profits = [float(t["profit"]) for t in trades]
    wins = sum(p > 0 for p in profits)
    losses = sum(p < 0 for p in profits)
    gross_profit = sum(p for p in profits if p > 0)
    gross_loss = abs(sum(p for p in profits if p < 0))

    # Use mark-to-market equity, not only closed-trade P&L, for drawdown.
    # The execution engine updates peak equity on every processed candle.
    max_drawdown = max(
        0.0,
        engine.peak_equity - min(
            engine.account.equity,
            engine.peak_equity,
        ),
    )
    # Reconstruct closed-equity drawdown as a lower bound for datasets where
    # the final position was closed after the last candle.
    running = float(config.starting_balance)
    peak = running
    for profit in profits:
        running += profit
        peak = max(peak, running)
        max_drawdown = max(max_drawdown, peak - running)

    return {
        "starting_balance": config.starting_balance,
        "ending_balance": account.balance,
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(trades) * 100.0 if trades else 0.0,
        "net_profit": account.balance - config.starting_balance,
        "max_drawdown": max_drawdown,
        "profit_factor": gross_profit / gross_loss if gross_loss > 0 else float("inf"),
        "total_commission": engine.total_commission,
        "trades": trades,
    }
