from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    rank: str
    suit: str


@dataclass
class GameState:
    my_cards: List[Card]
    table_cards: List[Card]
    opponent_cards_visible: List[Card]


def analyze_state(state: GameState) -> str:
    if not state.my_cards:
        return "هیچ کارتەکی دەست نەناسراوە."

    return (
        "کارتەکان ناسراون، بەڵام Game Engine ـی تایبەتی "
        "هێشتا پێویستی بە زانیاری یاسای یارییەکە هەیە."
    )
