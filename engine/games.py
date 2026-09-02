SUPPORTED_GAMES = [
    "tarneeb",
    "trix",
    "baloot",
    "basra",
    "jackaroo",
]


def is_supported(game_name: str) -> bool:
    return game_name.lower() in SUPPORTED_GAMES
