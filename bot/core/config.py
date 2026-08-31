import os
from dataclasses import dataclass


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True)
class Settings:
    app_name: str = "HMB FOREX AI V300"

    environment: str = os.getenv("HMB_ENV", "development")

    starting_balance: float = _float_env(
        "HMB_STARTING_BALANCE", 1000.0
    )

    risk_percent: float = _float_env(
        "HMB_RISK_PERCENT", 0.5
    )

    max_daily_loss_percent: float = _float_env(
        "HMB_MAX_DAILY_LOSS", 2.0
    )

    max_drawdown_percent: float = _float_env(
        "HMB_MAX_DRAWDOWN", 10.0
    )

    live_trading: bool = (
        os.getenv("HMB_LIVE_TRADING", "false").lower()
        == "true"
    )


settings = Settings()
