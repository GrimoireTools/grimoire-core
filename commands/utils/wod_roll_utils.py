from dataclasses import dataclass, field
from random import randint


@dataclass
class WodRollResult:
    pool: int
    difficulty: int
    has_specialty: bool
    use_willpower: bool
    dice: list[int] = field(default_factory=list)
    unbotch: bool = False
    successes: int = 0
    ones: int = 0

    @property
    def result(self) -> str:
        if self.successes > 0:
            return "Success"
        if self.is_botch:
            return "Botch"
        return "Failure"

    @property
    def is_botch(self) -> bool:
        return self.successes <= 0 and self.ones > 0 and not self.unbotch


def wod_roll(pool: int, difficulty: int = 6, has_specialty: bool = False, use_willpower: bool = False) -> WodRollResult:
    """Roll a WoD dice pool and return the result.

    - Each die >= difficulty counts as a success.
    - Each 1 subtracts one success.
    - With specialty, 10s count as 2 successes instead of 1.
    - Botch: net successes <= 0 and at least one 1 rolled.
    """
    result = WodRollResult(pool=pool, difficulty=difficulty, has_specialty=has_specialty, use_willpower=use_willpower)

    if pool <= 0:
        result.ones = 1  # 0-pool auto-botch
        return result

    dice = [randint(1, 10) for _ in range(pool)]
    result.dice = dice

    for die in dice:
        if die == 1:
            result.ones += 1
            result.successes -= 1
        elif die >= difficulty:
            bonus = 2 if (has_specialty and die == 10) else 1
            result.successes += bonus
            result.unbotch = True  # any success unbotches the roll

    if use_willpower:
        if result.successes <= 0:
            result.successes = 1
            result.unbotch = True
        else:
            result.successes +=1

    return result


# ── ANSI formatting ──────────────────────────────────────────────────────────

_RESET = "\033[0m"
_RED = "\033[1;31m"
_GREEN = "\033[1;32m"
_YELLOW = "\033[1;33m"
_WHITE = "\033[0;37m"


def _fmt_die(die: int, difficulty: int, has_specialty: bool) -> str:
    if die == 1:
        color = _RED
    elif has_specialty and die == 10:
        color = _YELLOW
    elif die >= difficulty:
        color = _GREEN
    else:
        color = _WHITE
    return f"{color}{die:>2}{_RESET}"


def format_roll(result: WodRollResult) -> str:
    """Return an ANSI-formatted string for display in a Discord ```ansi block."""
    dice_str = "  ".join(_fmt_die(d, result.difficulty, result.has_specialty) for d in result.dice)

    if result.pool <= 0:
        dice_str = f"{_RED}No dice (pool = 0){_RESET}"

    result_color = _GREEN if result.successes > 0 else _RED if result.is_botch else _WHITE
    result_line = f"{result_color}{result.result}{_RESET}"
    if result.successes > 0:
        result_line += f"  ({result_color}{result.successes} success{'es' if result.successes != 1 else ''}{_RESET})"

    specialty_note = "  ★ specialty (10s = 2 successes)" if result.has_specialty else ""
    willpower_note = "  ★ automatic success (willpower)" if result.use_willpower else ""

    return f"[ {dice_str} ]\n{result_line}{specialty_note}{willpower_note}"
