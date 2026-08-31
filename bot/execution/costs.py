from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionCosts:
    spread_pips: float = 1.0
    slippage_pips: float = 0.2
    commission_per_lot: float = 7.0
    pip_size: float = 0.0001


@dataclass(frozen=True)
class ExecutionResult:
    requested_price: float
    executed_price: float
    spread_price: float
    slippage_price: float
    commission: float


def calculate_execution(side, requested_price, lots, costs=None):
    costs = costs or ExecutionCosts()
    side = side.upper()

    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    if requested_price <= 0:
        raise ValueError("requested_price must be greater than 0")
    if lots <= 0:
        raise ValueError("lots must be greater than 0")

    spread = costs.spread_pips * costs.pip_size
    slippage = costs.slippage_pips * costs.pip_size

    half_spread = spread / 2.0

    if side == "BUY":
        executed = requested_price + half_spread + slippage
    else:
        executed = requested_price - half_spread - slippage

    commission = costs.commission_per_lot * lots

    return ExecutionResult(
        requested_price=requested_price,
        executed_price=executed,
        spread_price=spread,
        slippage_price=slippage,
        commission=round(commission, 2),
    )
