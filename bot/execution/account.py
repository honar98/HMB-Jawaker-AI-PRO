from dataclasses import dataclass


@dataclass
class Position:
    side: str
    entry: float
    size: float
    stop_loss: float
    take_profit: float
    contract_size: float = 100_000.0
    current_price: float | None = None

    def __post_init__(self):
        self.side = self.side.upper()

        if self.side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        if self.entry <= 0:
            raise ValueError("entry must be greater than 0")

        if self.size <= 0:
            raise ValueError("size must be greater than 0")

        if self.stop_loss <= 0 or self.take_profit <= 0:
            raise ValueError("SL/TP must be greater than 0")

        if self.contract_size <= 0:
            raise ValueError("contract_size must be greater than 0")

        if self.current_price is None:
            self.current_price = self.entry

    @property
    def units(self):
        return self.size * self.contract_size

    def unrealized_pnl(self, price=None):
        price = self.current_price if price is None else price

        if price <= 0:
            raise ValueError("price must be greater than 0")

        if self.side == "BUY":
            return (price - self.entry) * self.units

        return (self.entry - price) * self.units


class Account:
    def __init__(
        self,
        balance=1000.0,
        contract_size=100_000.0,
        max_open_positions=1,
    ):
        if balance <= 0:
            raise ValueError("Initial balance must be greater than 0")

        if contract_size <= 0:
            raise ValueError("contract_size must be greater than 0")

        if max_open_positions <= 0:
            raise ValueError("max_open_positions must be greater than 0")

        self.balance = float(balance)
        self.contract_size = float(contract_size)
        self.max_open_positions = int(max_open_positions)
        self.positions = []

    @property
    def floating_pnl(self):
        return sum(
            position.unrealized_pnl()
            for position in self.positions
        )

    @property
    def equity(self):
        return self.balance + self.floating_pnl

    def mark_price(self, price):
        if price <= 0:
            raise ValueError("price must be greater than 0")

        for position in self.positions:
            position.current_price = float(price)

        return self.equity

    def open_position(
        self,
        side,
        entry,
        size,
        stop_loss,
        take_profit,
    ):
        if len(self.positions) >= self.max_open_positions:
            raise ValueError("Maximum open positions reached")

        position = Position(
            side=side,
            entry=float(entry),
            size=float(size),
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            contract_size=self.contract_size,
            current_price=float(entry),
        )

        self.positions.append(position)
        return position

    def close_position(self, position, exit_price):
        if position not in self.positions:
            raise ValueError("Position is not open")

        if exit_price <= 0:
            raise ValueError("exit_price must be greater than 0")

        pnl = position.unrealized_pnl(exit_price)

        self.balance += pnl
        self.positions.remove(position)

        return pnl
