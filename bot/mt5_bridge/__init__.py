"""
HMB FOREX AI - MT5 Demo Bridge

Safe bridge interface.
Real order execution is intentionally disabled.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MT5Config:
    symbol: str = "EURUSD"
    demo_only: bool = True
    allow_real_orders: bool = False


class MT5DemoBridge:
    def __init__(self, config=None):
        self.config = config or MT5Config()
        self.connected = False

    def connect(self):
        if not self.config.demo_only:
            raise RuntimeError("Live MT5 mode is disabled")

        if self.config.allow_real_orders:
            raise RuntimeError("Real orders are disabled")

        self.connected = True
        return True

    def status(self):
        return {
            "connected": self.connected,
            "symbol": self.config.symbol,
            "demo_only": self.config.demo_only,
            "real_orders": False,
        }

    def get_price(self):
        if not self.connected:
            raise RuntimeError("MT5 Demo bridge is not connected")

        raise NotImplementedError(
            "Demo price provider is not configured yet"
        )

    def send_order(self, *args, **kwargs):
        raise RuntimeError(
            "REAL ORDER EXECUTION IS DISABLED"
        )


__all__ = ["MT5Config", "MT5DemoBridge"]
