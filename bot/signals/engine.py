from dataclasses import dataclass


@dataclass
class Signal:
    action: str
    score: int
    reason: list[str]


def analyze(
    trend: str,
    momentum: str,
    structure: str,
    volatility: str,
) -> Signal:
    score = 50
    reasons = []

    if trend == "bullish":
        score += 15
        reasons.append("Bullish trend")
    elif trend == "bearish":
        score -= 15
        reasons.append("Bearish trend")

    if momentum == "strong_buy":
        score += 15
        reasons.append("Strong bullish momentum")
    elif momentum == "strong_sell":
        score -= 15
        reasons.append("Strong bearish momentum")

    if structure == "bullish":
        score += 10
        reasons.append("Bullish market structure")
    elif structure == "bearish":
        score -= 10
        reasons.append("Bearish market structure")

    if volatility == "high":
        reasons.append("High volatility")

    score = max(0, min(100, score))

    if score >= 75:
        action = "BUY"
    elif score <= 25:
        action = "SELL"
    else:
        action = "WAIT"

    return Signal(
        action=action,
        score=score,
        reason=reasons,
    )
