from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    risk_percent: float = 0.5
    max_daily_loss_percent: float = 2.0
    max_drawdown_percent: float = 10.0
    max_positions: int = 1

    atr_stop_multiplier: float = 1.5
    atr_target_multiplier: float = 2.5


def calculate_position_size(
    balance: float,
    entry: float,
    stop_loss: float,
    risk_percent: float = 0.5,
) -> float:
    if balance <= 0:
        raise ValueError("balance must be greater than 0")

    if entry <= 0 or stop_loss <= 0:
        raise ValueError("prices must be greater than 0")

    if risk_percent <= 0:
        raise ValueError("risk_percent must be greater than 0")

    distance = abs(entry - stop_loss)

    if distance <= 0:
        raise ValueError("entry and stop_loss cannot be equal")

    risk_amount = balance * (risk_percent / 100.0)

    return risk_amount / distance


def calculate_sl_tp(
    entry: float,
    atr_value: float,
    side: str,
    config: RiskConfig | None = None,
):
    config = config or RiskConfig()

    if entry <= 0:
        raise ValueError("entry must be greater than 0")

    if atr_value <= 0:
        raise ValueError("ATR must be greater than 0")

    side = side.upper()

    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")

    stop_distance = atr_value * config.atr_stop_multiplier
    target_distance = atr_value * config.atr_target_multiplier

    if side == "BUY":
        stop_loss = entry - stop_distance
        take_profit = entry + target_distance
    else:
        stop_loss = entry + stop_distance
        take_profit = entry - target_distance

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_distance": stop_distance,
        "reward_distance": target_distance,
        "risk_reward": (
            target_distance / stop_distance
        ),
    }
