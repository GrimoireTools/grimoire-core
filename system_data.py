from typing import Literal


Profs = Literal["None", "Half", "Full", "Expert"]
BASE_PROF_BONUS = 3
PROF_BONUSES: dict[Profs, int] = {
    "None": 0,
    "Half": BASE_PROF_BONUS // 2,
    "Full": BASE_PROF_BONUS,
    "Expert": BASE_PROF_BONUS * 2
}

Attr = Literal["Str", "Dex", "Con", "Int", "Wis", "Cha"]
ATTRS: list[Attr] = ["Str", "Dex", "Con", "Int", "Wis", "Cha"]
