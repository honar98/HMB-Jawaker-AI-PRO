from dataclasses import dataclass


@dataclass
class Trade:
    entry: float
    exit: float
    side: str
    profit: float


def calculate_trade(entry: float, exit: float, side: str) -> Trade:
    if entry <= 0 or exit <= 0:
        raise ValueError("prices must be greater than 0")

    side = side.upper()

    if side == "BUY":
        profit = exit - entry
    elif side == "SELL":
        profit = entry - exit
    else:
        raise ValueError("side must be BUY or SELL")

    return Trade(
        entry=entry,
        exit=exit,
        side=side,
        profit=profit,
    )


def backtest(trades):
    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "net_profit": 0.0,
            "max_drawdown": 0.0,
            "profit_factor": 0.0,
        }

    profits = [trade.profit for trade in trades]

    wins = sum(1 for p in profits if p > 0)
    losses = sum(1 for p in profits if p < 0)

    gross_profit = sum(p for p in profits if p > 0)
    gross_loss = abs(sum(p for p in profits if p < 0))

    balance = 0.0
    peak = 0.0
    max_drawdown = 0.0

    for profit in profits:
        balance += profit
        peak = max(peak, balance)

        drawdown = peak - balance
        max_drawdown = max(max_drawdown, drawdown)

    total = len(trades)

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / total) * 100.0,
        "net_profit": sum(profits),
        "max_drawdown": max_drawdown,
        "profit_factor": (
            gross_profit / gross_loss
            if gross_loss > 0
            else float("inf")
        ),
    }
