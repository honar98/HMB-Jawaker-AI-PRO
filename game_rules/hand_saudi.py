from strategy.card_engine import (
    normalize_cards,
    find_sequences,
    find_sets,
)

def card_value(card):
    rank = card["rank"]

    if rank == "A":
        return 11

    if rank == "JOKER":
        return 15

    if rank in ("K", "Q", "J"):
        return 10

    return int(rank)


def opening_value(cards):
    return sum(card_value(c) for c in cards)


def can_make_basic_meld(cards):
    """
    Detect whether visible cards contain the beginning
    of a valid set/sequence.
    """
    sequences = find_sequences(cards)
    sets = find_sets(cards)

    return bool(
        any(len(x) >= 3 for x in sequences)
        or any(len(x) >= 3 for x in sets)
    )


def evaluate_opening(cards, minimum=51):
    cards = normalize_cards(cards)

    value = opening_value(cards)

    return {
        "value": value,
        "minimum": minimum,
        "can_open_by_value": value >= minimum,
        "has_basic_meld": can_make_basic_meld(cards),
    }


def rules_summary():
    return {
        "players": "2-5",
        "deck": 106,
        "initial_cards": 14,
        "first_player_cards": 15,
        "minimum_opening": 51,
        "rounds": 5,
        "partnership": True,
    }
