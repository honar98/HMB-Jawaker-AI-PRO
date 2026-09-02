from strategy.card_engine import analyze_hand
from game_rules.hand_saudi import evaluate_opening


def run_strategy(
    game,
    hand,
    discarded=None,
    opponent_info=None,
    opening_minimum=51,
):
    """
    Deterministic strategy layer.

    Currently optimized for Hand / Saudi Hand style games.
    Other games can plug their own rule engine later.
    """

    game_name = (game or "").lower()

    result = {
        "game": game,
        "engine": "HMB PRO Strategy Engine",
        "legal_move": None,
        "best_discard": None,
        "alternatives": [],
        "analysis": None,
    }

    analysis = analyze_hand(
        hand,
        discarded=discarded,
        opponent_info=opponent_info,
    )

    result["analysis"] = analysis

    if not analysis.get("ok"):
        return result

    # Rummy / Hand-family games.
    if any(
        name in game_name
        for name in (
            "hand",
            "saudi",
            "rummy",
            "concan",
        )
    ):
        cards = analysis

        result["best_discard"] = cards.get("best_discard")
        result["alternatives"] = cards.get("alternatives", [])

        return result

    # Other games currently use the vision model's move,
    # while the deterministic framework remains ready.
    return result
