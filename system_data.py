from typing import Literal

Attribute = Literal[
    "Strength",
    "Dexterity",
    "Stamina",
    "Charisma",
    "Manipulation",
    "Appearance",
    "Perception",
    "Intelligence",
    "Wits",
]

ATTRIBUTES: list[Attribute] = list(
    Attribute.__args__)  # type: ignore[attr-defined]

Ability = str

PREDEFINED_ABILITIES: list[Ability] = [
    # Talents
    "Alertness", "Athletics", "Awareness", "Brawl", "Empathy",
    "Expression", "Intimidation", "Leadership", "Streetwise", "Subterfuge",
    # Skills
    "Animal Ken", "Crafts", "Drive", "Etiquette", "Firearms",
    "Larceny", "Melee", "Performance", "Stealth", "Survival",
    # Knowledges
    "Academics", "Computer", "Finance", "Investigation", "Law",
    "Linguistics", "Medicine", "Occult", "Politics", "Science",

]

Resource = str

CharType = Literal["Vampire", "Hunter", "Mage"]

CHARACTER_TYPES: list[CharType] = ["Vampire", "Hunter", "Mage"]

DEFAULT_RESOURCES: dict[CharType, dict[str, int]] = {
    "Vampire": {"Blood Pool": 10, "Willpower": 7},
    "Hunter": {"Willpower": 7, "Conviction": 3},
    "Mage": {"Quintessence": 5, "Paradox": 0, "Willpower": 7},
}
