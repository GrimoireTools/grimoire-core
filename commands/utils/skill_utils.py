from dndice import basic, compile

ALTERNATE = True
c_d20 = compile("1d20")


def nat_20_1_message(dice_result: int):
    if dice_result == 20:
        return "**Nat 20!** "
    elif dice_result == 1:
        return "**Nat 1!** "
    else:
        return ""


def fb(bonus: int, bold: bool = False) -> str:
    """Format bonus numbers with colors."""
    b = 1 if bold else 0
    BLUE = f"\033[{b};34m"
    RED = f"\033[{b};31m"
    YELLOW = f"\033[{b};33m"
    RESET = "\033[0m"
    color = YELLOW if bonus == 0 else RED if bonus < 0 else BLUE
    return f"{color}{bonus:+}{RESET}"


def _d20() -> int:
    """
    Rolls a d20 and returns the result.
    """
    return int(basic(c_d20))


def format_diceroll(dice: int, total: int, bold: bool = True, underline: bool = False) -> str:
    b = 1 if bold else 0
    b = 4 if underline else b
    RED = f"\033[{b};31m"
    CYAN = f"\033[{b};36m"
    WHITE = f"\033[{b};37m"
    RESET = f"\033[0m"
    color = RED if dice == 1 else CYAN if dice == 20 else WHITE
    return f"{color}{total}{RESET}"
