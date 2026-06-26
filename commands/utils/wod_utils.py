FILLED = "●"
EMPTY = "○"


def dots(value: int, max_dots: int = 5) -> str:
    """Returns a dot string representing a WoD trait value.

    Examples:
        dots(3)    → '●●●○○'
        dots(6, 8) → '●●●●●●○○'
        dots(0)    → '○○○○○'
    """
    filled = min(max(value, 0), max_dots)
    return FILLED * filled + EMPTY * (max_dots - filled)
