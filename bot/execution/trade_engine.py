from dataclasses import dataclass

from .account import Account, Position
from .costs import calculate_execution, ExecutionCosts
from .risk_engine import (
    calculate_position_size,
    check_account_limits,
    RiskConfig,
)


@dataclass(frozen=True)
class TradeResult:
    opened: bool
    side: str
    entry: float
    size: float
    stop_loss: float
    take_profit: float
    reason: str


@dataclass(frozen=True)
class CloseResult:
    closed: bool
    side: str
    exit_price: float
    pnl: float
    commission: float
    net_pnl: float
    reason: str


class TradeEngine:
    def __init__(
        self,
        account=None,
        execution_costs=None,
        risk_config=None,
    ):
        self.account = account or Account(1000.0)
        self.execution_costs = execution_costs or ExecutionCosts()
        self.risk_config = risk_config or RiskConfig()

        self.starting_balance = self.account.balance
        self.daily_start_equity = self.account.equity
        self.peak_equity = self.account.equity
        self.daily_start_equity = self.account.equity
        self._current_day = None

        self.closed_trades = []
        self.total_commission = 0.0

    def start_new_day(self, timestamp):
        """Reset the daily loss baseline when the UTC trading day changes."""
        day = timestamp.date() if hasattr(timestamp, "date") else str(timestamp)[:10]
        if self._current_day != day:
            self._current_day = day
            self.daily_start_equity = self.account.equity

    def _update_peak(self):
        self.peak_equity = max(
            self.peak_equity,
            self.account.equity,
        )

    def open_trade(
        self,
        side,
        price,
        stop_loss,
        take_profit,
    ):
        side = side.upper()

        if side not in ("BUY", "SELL"):
            return TradeResult(
                False,
                side,
                price,
                0.0,
                stop_loss,
                take_profit,
                "Invalid side",
            )

        if price <= 0:
            return TradeResult(
                False, side, price, 0.0,
                stop_loss, take_profit,
                "Invalid price",
            )

        # Validate SL/TP direction.
        if side == "BUY":
            if stop_loss >= price:
                return TradeResult(
                    False, side, price, 0.0,
                    stop_loss, take_profit,
                    "BUY stop_loss must be below entry",
                )
            if take_profit <= price:
                return TradeResult(
                    False, side, price, 0.0,
                    stop_loss, take_profit,
                    "BUY take_profit must be above entry",
                )

        else:
            if stop_loss <= price:
                return TradeResult(
                    False, side, price, 0.0,
                    stop_loss, take_profit,
                    "SELL stop_loss must be above entry",
                )
            if take_profit >= price:
                return TradeResult(
                    False, side, price, 0.0,
                    stop_loss, take_profit,
                    "SELL take_profit must be below entry",
                )

        self._update_peak()

        allowed, reason = check_account_limits(
            self.account.equity,
            self.daily_start_equity,
            self.peak_equity,
            self.risk_config,
        )

        if not allowed:
            return TradeResult(
                False,
                side,
                price,
                0.0,
                stop_loss,
                take_profit,
                reason,
            )

        risk = calculate_position_size(
            self.account.equity,
            price,
            stop_loss,
            self.risk_config,
            free_margin=self.account.equity,
        )

        if not risk.allowed:
            return TradeResult(
                False,
                side,
                price,
                0.0,
                stop_loss,
                take_profit,
                risk.reason,
            )

        execution = calculate_execution(
            side,
            price,
            risk.position_size,
            self.execution_costs,
        )

        position = self.account.open_position(
            side,
            execution.executed_price,
            risk.position_size,
            stop_loss,
            take_profit,
        )

        return TradeResult(
            True,
            side,
            position.entry,
            position.size,
            position.stop_loss,
            position.take_profit,
            "Trade opened",
        )

    def _exit_price_for_market(self, position, market_price):
        """
        Convert a mid/market price to the executable opposite-side price.

        BUY closes against BID.
        SELL closes against ASK.

        Slippage is applied separately by calculate_execution().
        """
        spread = (
            self.execution_costs.spread_pips
            * self.execution_costs.pip_size
        )

        half_spread = spread / 2.0

        if position.side == "BUY":
            return market_price - half_spread

        return market_price + half_spread

    def close_trade(
        self,
        position,
        requested_price,
        reason="Manual close",
    ):
        if position not in self.account.positions:
            return CloseResult(
                False,
                position.side,
                requested_price,
                0.0,
                0.0,
                0.0,
                "Position is not open",
            )

        execution_side = "SELL" if position.side == "BUY" else "BUY"

        execution = calculate_execution(
            execution_side,
            requested_price,
            position.size,
            self.execution_costs,
        )

        pnl = self.account.close_position(
            position,
            execution.executed_price,
        )

        commission = execution.commission

        # Commission is round-turn and is charged when the trade closes.
        self.account.balance -= commission
        self.total_commission += commission

        net_pnl = pnl - commission

        result = CloseResult(
            True,
            position.side,
            execution.executed_price,
            pnl,
            commission,
            net_pnl,
            reason,
        )

        self.closed_trades.append(result)
        self._update_peak()

        return result

    def update_market(self, market_price):
        if market_price <= 0:
            raise ValueError("market_price must be greater than 0")

        executable_prices = []

        for position in list(self.account.positions):
            exit_market_price = self._exit_price_for_market(
                position,
                market_price,
            )

            position.current_price = exit_market_price
            executable_prices.append(exit_market_price)

        self._update_peak()

        return {
            "balance": self.account.balance,
            "floating_pnl": self.account.floating_pnl,
            "equity": self.account.equity,
            "peak_equity": self.peak_equity,
            "open_positions": len(self.account.positions),
        }

    def process_candle(
        self,
        open_price,
        high,
        low,
        close,
    ):
        """
        Process one OHLC candle.

        Conservative rule:
        If both SL and TP are touched inside the same candle,
        SL is assumed to happen first.

        This avoids optimistic backtest bias.
        """
        if not (
            open_price > 0
            and high > 0
            and low > 0
            and close > 0
        ):
            raise ValueError("OHLC prices must be greater than 0")

        if high < low:
            raise ValueError("high cannot be below low")

        if open_price < low or open_price > high:
            raise ValueError("open must be inside candle range")

        if close < low or close > high:
            raise ValueError("close must be inside candle range")

        events = []

        for position in list(self.account.positions):
            # Gap-aware execution: if the market opens beyond SL/TP, a real
            # stop/limit order cannot normally be filled at the old level.
            if position.side == "BUY":
                if open_price <= position.stop_loss:
                    result = self.close_trade(
                        position, open_price, reason="STOP_LOSS_GAP"
                    )
                    events.append(result)
                    continue
                if open_price >= position.take_profit:
                    result = self.close_trade(
                        position, open_price, reason="TAKE_PROFIT_GAP"
                    )
                    events.append(result)
                    continue

                hit_sl = low <= position.stop_loss
                hit_tp = high >= position.take_profit
            else:
                if open_price >= position.stop_loss:
                    result = self.close_trade(
                        position, open_price, reason="STOP_LOSS_GAP"
                    )
                    events.append(result)
                    continue
                if open_price <= position.take_profit:
                    result = self.close_trade(
                        position, open_price, reason="TAKE_PROFIT_GAP"
                    )
                    events.append(result)
                    continue

                hit_sl = high >= position.stop_loss
                hit_tp = low <= position.take_profit

            if hit_sl:
                result = self.close_trade(
                    position,
                    position.stop_loss,
                    reason=(
                        "STOP_LOSS"
                        if not hit_tp
                        else "STOP_LOSS_CONSERVATIVE"
                    ),
                )
                events.append(result)
                continue

            if hit_tp:
                result = self.close_trade(
                    position,
                    position.take_profit,
                    reason="TAKE_PROFIT",
                )
                events.append(result)
                continue

            # No exit: mark position to executable close price.
            self.update_market(close)

        self._update_peak()

        return {
            "events": events,
            "balance": self.account.balance,
            "floating_pnl": self.account.floating_pnl,
            "equity": self.account.equity,
            "peak_equity": self.peak_equity,
            "open_positions": len(self.account.positions),
        }

    def update(self):
        self._update_peak()

        return {
            "balance": self.account.balance,
            "floating_pnl": self.account.floating_pnl,
            "equity": self.account.equity,
            "peak_equity": self.peak_equity,
            "open_positions": len(self.account.positions),
            "closed_trades": len(self.closed_trades),
            "total_commission": self.total_commission,
        }
