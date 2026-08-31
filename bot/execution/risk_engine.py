from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RiskConfig:
    risk_percent: float = 0.5
    max_daily_loss_percent: float = 2.0
    max_drawdown_percent: float = 10.0

    pip_size: float = 0.0001
    pip_value_per_lot: float = 10.0

    contract_size: float = 100_000.0
    min_lot: float = 0.01
    max_lot: float = 5.0
    lot_step: float = 0.01

    leverage: float = 100.0
    margin_buffer_percent: float = 20.0


@dataclass(frozen=True)
class RiskResult:
    allowed: bool
    risk_amount: float
    stop_distance: float
    stop_pips: float
    position_size: float
    estimated_margin: float
    reason: str


def _round_down(value, step):
    if step <= 0:
        raise ValueError("lot_step must be greater than 0")

    steps = math.floor((value + 1e-12) / step)
    return round(steps * step, 10)


def calculate_position_size(
    balance,
    entry,
    stop_loss,
    config=None,
    free_margin=None,
):
    config = config or RiskConfig()

    if balance <= 0:
        raise ValueError("balance must be greater than 0")

    if entry <= 0 or stop_loss <= 0:
        raise ValueError("prices must be greater than 0")

    if config.risk_percent <= 0:
        raise ValueError("risk_percent must be greater than 0")

    if config.pip_size <= 0:
        raise ValueError("pip_size must be greater than 0")

    if config.pip_value_per_lot <= 0:
        raise ValueError("pip_value_per_lot must be greater than 0")

    if config.contract_size <= 0:
        raise ValueError("contract_size must be greater than 0")

    if config.leverage <= 0:
        raise ValueError("leverage must be greater than 0")

    if config.min_lot <= 0:
        raise ValueError("min_lot must be greater than 0")

    if config.max_lot < config.min_lot:
        raise ValueError("max_lot must be >= min_lot")

    if config.lot_step <= 0:
        raise ValueError("lot_step must be greater than 0")

    distance = abs(entry - stop_loss)

    if distance <= 0:
        return RiskResult(
            False, 0.0, 0.0, 0.0, 0.0, 0.0,
            "Stop loss must differ from entry",
        )

    risk_amount = balance * config.risk_percent / 100.0
    stop_pips = distance / config.pip_size

    raw_lots = risk_amount / (
        stop_pips * config.pip_value_per_lot
    )

    lots = _round_down(
        min(raw_lots, config.max_lot),
        config.lot_step,
    )

    if lots < config.min_lot:
        return RiskResult(
            False,
            risk_amount,
            distance,
            stop_pips,
            0.0,
            0.0,
            "Calculated position is below minimum lot",
        )

    estimated_margin = (
        lots * config.contract_size * entry
    ) / config.leverage

    if free_margin is not None:
        if free_margin < 0:
            raise ValueError("free_margin cannot be negative")

        required_margin = (
            estimated_margin
            * (1.0 + config.margin_buffer_percent / 100.0)
        )

        if free_margin < required_margin:
            return RiskResult(
                False,
                risk_amount,
                distance,
                stop_pips,
                lots,
                estimated_margin,
                "Insufficient free margin",
            )

    return RiskResult(
        True,
        round(risk_amount, 2),
        distance,
        stop_pips,
        lots,
        round(estimated_margin, 2),
        "Risk checks passed",
    )


def check_account_limits(
    equity,
    daily_start_equity,
    peak_equity,
    config=None,
):
    config = config or RiskConfig()

    if equity <= 0:
        return False, "Invalid equity"

    if daily_start_equity <= 0:
        return False, "Invalid daily start equity"

    if peak_equity <= 0:
        return False, "Invalid peak equity"

    daily_loss = max(
        0.0,
        daily_start_equity - equity,
    )

    daily_limit = (
        daily_start_equity
        * config.max_daily_loss_percent
        / 100.0
    )

    drawdown = max(
        0.0,
        peak_equity - equity,
    )

    drawdown_limit = (
        peak_equity
        * config.max_drawdown_percent
        / 100.0
    )

    if daily_loss >= daily_limit:
        return False, "Maximum daily loss reached"

    if drawdown >= drawdown_limit:
        return False, "Maximum drawdown reached"

    return True, "Account limits passed"
