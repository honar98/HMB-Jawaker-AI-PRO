from collections import Counter, defaultdict
import re

RANKS = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14,
}

SUITS = {"♥", "♦", "♣", "♠"}

def parse_card(card):
    if not isinstance(card, str):
        return None

    card = card.strip()

    m = re.match(r"^(10|[2-9JQKA])([♥♦♣♠])$", card)
    if not m:
        if "JOKER" in card.upper() or "🃏" in card:
            return {"rank": "JOKER", "value": 0, "suit": None}
        return None

    rank, suit = m.groups()

    return {
        "rank": rank,
        "value": RANKS[rank],
        "suit": suit,
    }


def normalize_cards(cards):
    result = []

    for card in cards or []:
        parsed = parse_card(card)
        if parsed:
            result.append(parsed)

    return result


def card_key(card):
    return f"{card['rank']}{card['suit'] or ''}"


def find_sequences(cards):
    """
    Find same-suit consecutive runs.
    """
    groups = defaultdict(list)

    for c in cards:
        if c["rank"] == "JOKER":
            continue
        groups[c["suit"]].append(c)

    sequences = []

    for suit, suit_cards in groups.items():
        suit_cards.sort(key=lambda x: x["value"])

        current = []

        for card in suit_cards:
            if not current:
                current = [card]
                continue

            if card["value"] == current[-1]["value"] + 1:
                current.append(card)
            else:
                if len(current) >= 2:
                    sequences.append(current)
                current = [card]

        if len(current) >= 2:
            sequences.append(current)

    return sequences


def find_sets(cards):
    """
    Find same-rank groups across suits.
    """
    groups = defaultdict(list)

    for c in cards:
        if c["rank"] == "JOKER":
            continue
        groups[c["rank"]].append(c)

    return [
        group
        for group in groups.values()
        if len(group) >= 2
    ]


def card_meld_potential(card, cards):
    """
    Higher score = more useful to keep.
    """
    if card["rank"] == "JOKER":
        return 100

    score = 0

    same_rank = [
        c for c in cards
        if c["rank"] == card["rank"]
        and c["suit"] != card["suit"]
    ]

    # Same-rank set potential.
    if same_rank:
        score += 35 * len(same_rank)

    # Same-suit sequence potential.
    for c in cards:
        if c["suit"] != card["suit"]:
            continue

        if c["rank"] == "JOKER":
            continue

        distance = abs(c["value"] - card["value"])

        if distance == 1:
            score += 28
        elif distance == 2:
            score += 12

    # High cards are valuable but also expensive to hold.
    score += min(card["value"], 14)

    return score


def discard_score(card, cards, discarded, opponent_info=None):
    """
    Lower score = better discard candidate.

    This is deterministic strategy, not random AI guessing.
    """
    if card["rank"] == "JOKER":
        return 9999

    score = 0

    # Preserve meld potential.
    score += card_meld_potential(card, cards) * 2.2

    # High-value cards are dangerous to keep late in the round.
    score -= card["value"] * 1.5

    # If this exact card has already appeared frequently,
    # it is generally less useful to hold.
    key = card_key(card)

    seen = Counter(
        card_key(c)
        for c in normalize_cards(discarded or [])
    )

    score -= min(seen.get(key, 0) * 8, 24)

    # Opponent observations.
    for opponent in opponent_info or []:
        if not isinstance(opponent, dict):
            continue

        useful = opponent.get("useful_cards", [])

        if key in useful:
            score += 70

        wanted_suits = opponent.get("wanted_suits", [])

        if card["suit"] in wanted_suits:
            score += 30

    return score


def rank_discards(hand, discarded=None, opponent_info=None):
    cards = normalize_cards(hand)

    if not cards:
        return []

    candidates = []

    for card in cards:
        score = discard_score(
            card,
            cards,
            discarded,
            opponent_info
        )

        candidates.append({
            "card": card_key(card),
            "score": round(score, 2),
        })

    candidates.sort(key=lambda x: x["score"])

    return candidates


def best_discard(hand, discarded=None, opponent_info=None):
    ranked = rank_discards(
        hand,
        discarded,
        opponent_info
    )

    return ranked[0] if ranked else None


def analyze_hand(hand, discarded=None, opponent_info=None):
    cards = normalize_cards(hand)

    if not cards:
        return {
            "ok": False,
            "reason": "No readable cards"
        }

    sequences = find_sequences(cards)
    sets = find_sets(cards)
    ranked = rank_discards(
        hand,
        discarded,
        opponent_info
    )

    return {
        "ok": True,
        "card_count": len(cards),
        "sequence_count": len(sequences),
        "set_count": len(sets),
        "best_discard": ranked[0] if ranked else None,
        "alternatives": ranked[1:4],
    }
