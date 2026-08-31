from collections import defaultdict
from datetime import datetime


def analyze_performance(trades):
    if not trades:
        return {
            "total_trades": 0,
            "buy_trades": 0,
            "sell_trades": 0,
            "wins": 0,
            "losses": 0,
            "net_profit": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "max_consecutive_losses": 0,
            "by_side": {},
            "by_month": {},
            "exit_reasons": {},
        }

    wins = [t for t in trades if t["profit"] > 0]
    losses = [t for t in trades if t["profit"] < 0]

    buy = [t for t in trades if t["side"] == "BUY"]
    sell = [t for t in trades if t["side"] == "SELL"]

    max_loss_streak = 0
    loss_streak = 0

    for trade in trades:
        if trade["profit"] < 0:
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
        else:
            loss_streak = 0

    by_side = {}

    for name, group in (("BUY", buy), ("SELL", sell)):
        group_wins = [t for t in group if t["profit"] > 0]
        group_losses = [t for t in group if t["profit"] < 0]

        gross_profit = sum(t["profit"] for t in group_wins)
        gross_loss = abs(sum(t["profit"] for t in group_losses))

        by_side[name] = {
            "trades": len(group),
            "wins": len(group_wins),
            "losses": len(group_losses),
            "win_rate": (
                len(group_wins) / len(group) * 100
                if group else 0.0
            ),
            "net_profit": sum(t["profit"] for t in group),
            "profit_factor": (
                gross_profit / gross_loss
                if gross_loss > 0
                else float("inf")
            ),
        }

    monthly = defaultdict(list)

    for trade in trades:
        time_value = trade["time"]

        try:
            month = datetime.fromisoformat(
                time_value.replace("Z", "+00:00")
            ).strftime("%Y-%m")
        except ValueError:
            month = str(time_value)[:7]

        monthly[month].append(trade)

    by_month = {}

    for month, group in sorted(monthly.items()):
        group_wins = [t for t in group if t["profit"] > 0]
        group_losses = [t for t in group if t["profit"] < 0]

        gross_profit = sum(t["profit"] for t in group_wins)
        gross_loss = abs(sum(t["profit"] for t in group_losses))

        by_month[month] = {
            "trades": len(group),
            "wins": len(group_wins),
            "losses": len(group_losses),
            "win_rate": (
                len(group_wins) / len(group) * 100
                if group else 0.0
            ),
            "net_profit": sum(t["profit"] for t in group),
            "profit_factor": (
                gross_profit / gross_loss
                if gross_loss > 0
                else float("inf")
            ),
        }

    exit_reasons = defaultdict(int)

    for trade in trades:
        exit_reasons[trade["reason"]] += 1

    return {
        "total_trades": len(trades),
        "buy_trades": len(buy),
        "sell_trades": len(sell),
        "wins": len(wins),
        "losses": len(losses),
        "net_profit": sum(t["profit"] for t in trades),
        "average_win": (
            sum(t["profit"] for t in wins) / len(wins)
            if wins else 0.0
        ),
        "average_loss": (
            sum(t["profit"] for t in losses) / len(losses)
            if losses else 0.0
        ),
        "max_consecutive_losses": max_loss_streak,
        "by_side": by_side,
        "by_month": dict(by_month),
        "exit_reasons": dict(exit_reasons),
    }
