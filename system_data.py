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

ATTRIBUTES: list[Attribute] = [
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

Ability = str

PREDEFINED_ABILITIES: list[Ability] = [
    # Talents
    "Alertness",
    "Art",
    "Athletics",
    "Awareness",
    "Brawl",
    "Dodge",
    "Empathy",
    "Expression",
    "Intimidation",
    "Intuition",
    "Leadership",
    "Streetwise",
    "Subterfuge",
    # Skills
    "Animal Ken",
    "Crafts",
    "Demolitions",
    "Drive",
    "Etiquette",
    "Firearms",
    "Larceny",
    "Martial Arts",
    "Meditation",
    "Melee",
    "Performance",
    "Research Sk",
    "Security",
    "Stealth",
    "Survival",
    "Technology Sk",
    # Knowledges
    "Academics",
    "Bureaucracy",
    "Computer",
    "Cosmology",
    "Enigmas",
    "Esoterica",
    "Finance",
    "Investigation",
    "Law",
    "Linguistics",
    "Medicine",
    "Occult",
    "Politics",
    "Research Kn",
    "Science",
    "Technology Kn"
]

TALENTS: list[Ability] = PREDEFINED_ABILITIES[:13]
SKILLS: list[Ability] = PREDEFINED_ABILITIES[13:29]
KNOWLEDGES: list[Ability] = PREDEFINED_ABILITIES[29:]

Resource = str

CharType = Literal["Vampire", "Hunter", "Mage"]

CHARACTER_TYPES: list[CharType] = ["Vampire", "Hunter", "Mage"]

DEFAULT_RESOURCES: dict[CharType, dict[str, int]] = {
    "Vampire": {"XP": 0, "Blood Pool": 10, "Willpower": 7},
    "Hunter": {"XP": 0, "Willpower": 7, "Conviction": 3},
    "Mage": {"XP": 0, "Quintessence": 5, "Paradox": 0, "Willpower": 7},
}

SUB_CHARACTER_TYPES: dict[CharType, dict[str, str]] = {
    "Vampire": {"Clan": "", "Generation": "11"},
    "Hunter": {"Virtue": "", "Creed": ""},
    "Mage": {"Affinity": "", "Paradigm": ""}
}

VampireClans: list[str] = [
    "Assamita",
    "Brujah",
    "Gangrel",
    "Giovanni",
    "Lasombra",
    "Malkavian",
    "Nosferatu",
    "Ravnos",
    "Seguidor de Set",
    "Toreador",
    "Tremere",
    "Tzimisce",
    "Ventrue",
]

HunterVirtues: list[str] = [
    "Mercy",
    "Vision",
    "Zeal",
]

HunterCreeds: list[str] = [
    #Mercy
    "Innocence",
    "Martyrdom",
    "Redemption",
    #Vision
    "Visionary"
    #Zeal
    "Defense",
    "Judgment",
    "Vengeance",
]

MageAffinity: list[str] = [
    "Correspondence",
    "Entropy",
    "Forces",
    "Life",
    "Matter",
    "Mind",
    "Prime",
    "Spirit",
    "Time",
]

MageParadigm: list[str] = [
    "A Mechanistic Cosmos",
    "A World of Gods and Monsters",
    "Bring Back the Golden Age!",
    "Creation's Divine and Alive",
    "Divine Order and Earthly Chaos",
    "Everything is Chaos",
    "Everything is Data",
    "Everything's an Illusion, Prison, or Mistake",
    "It's All Good - Have Faith!",
    "Might is Right",
    "One-Way Trip to Oblivion",
    "Tech Holds All Answers"
]

SUBTYPE_VALUE_SOURCE: dict[str, list[str]] = {
    "Clan": VampireClans,
    "Affinity": MageAffinity,
    "Virtue": HunterVirtues,
    "Creed": HunterCreeds,
    "Paradigm": MageParadigm,
}
