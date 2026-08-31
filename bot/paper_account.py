from dataclasses import dataclass, asdict


@dataclass
class PaperPosition:
    side: str
    entry: float
    size: float
    stop_loss: float
    take_profit: float
    opened_at: str


class PaperAccount:
    def __init__(self, starting_balance=10000.0):
        self.starting_balance = float(starting_balance)
        self.balance = float(starting_balance)
        self.position = None
        self.history = []

    @property
    def equity(self):
        if self.position is None:
            return self.balance
        return self.balance

    def open_buy(self, price, size, stop_loss, take_profit, timestamp):
        if self.position is not None:
            return False, "Position already open"

        self.position = PaperPosition(
            side="BUY",
            entry=float(price),
            size=float(size),
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            opened_at=timestamp,
        )
        return True, "BUY opened"

    def update(self, price, timestamp):
        if self.position is None:
            return None

        p = self.position

        if price <= p.stop_loss:
            return self.close(price, timestamp, "STOP LOSS")

        if price >= p.take_profit:
            return self.close(price, timestamp, "TAKE PROFIT")

        return None

    def close(self, price, timestamp, reason="MANUAL"):
        if self.position is None:
            return None

        p = self.position

        # EURUSD: approximate P/L using $10 per pip per 1.00 lot.
        pip_value = 10.0
        pip_size = 0.0001

        pnl = ((float(price) - p.entry) / pip_size) * pip_value * p.size

        self.balance += pnl

        trade = {
            "side": p.side,
            "entry": p.entry,
            "exit": float(price),
            "size": p.size,
            "stop_loss": p.stop_loss,
            "take_profit": p.take_profit,
            "pnl": round(pnl, 2),
            "balance": round(self.balance, 2),
            "opened_at": p.opened_at,
            "closed_at": timestamp,
            "reason": reason,
        }

        self.history.append(trade)
        self.position = None

        return trade

    def status(self):
        return {
            "mode": "PAPER TRADING",
            "starting_balance": round(self.starting_balance, 2),
            "balance": round(self.balance, 2),
            "equity": round(self.equity, 2),
            "open_position": (
                asdict(self.position)
                if self.position else None
            ),
            "closed_trades": len(self.history),
            "history": self.history[-20:],
        }
