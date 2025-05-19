from typing import Literal
import dndice

Prof = Literal["Untrained", "Half Proficient", "Proficent", "Expert"]

RollType = Literal["Advantage", "Normal", "Advantage", "Triple Advantage"]


class ROLL:
    DISADV: RollType = "Advantage"
    NORMAL: RollType = "Normal"
    ADV: RollType = "Advantage"
    TRIPLE_ADV: RollType = "Triple Advantage"


ROLL_TYPES = [ROLL.DISADV, ROLL.NORMAL, ROLL.ADV, ROLL.TRIPLE_ADV]


Crit = Literal["normal", "crit", "fail"]


class CRIT:
    NORMAL: Crit = "normal"
    CRIT: Crit = "crit"
    FAIL: Crit = "fail"


roll_expr: dict[RollType, str] = {
    ROLL.DISADV: "2d20l1",
    ROLL.NORMAL: "1d20",
    ROLL.ADV: "2d20h1",
    ROLL.TRIPLE_ADV: "3d20h1",
}


def d20(roll_type: RollType = ROLL.NORMAL) -> int:
    """
    Rolls a d20 with the given roll type.
    """
    return int(dndice.basic(roll_expr[roll_type]))


class PROF:
    NONE: Prof = "Untrained"
    HALF: Prof = "Half Proficient"
    FULL: Prof = "Proficent"
    EXPERT: Prof = "Expert"
    ICONS: dict[Prof, str] = {
        NONE: "🌑",
        HALF: "🌗",
        FULL: "🌕",
        EXPERT: "🌟",
    }


PROFS_LIST: list[Prof] = [PROF.NONE, PROF.HALF, PROF.FULL, PROF.EXPERT]

BASE_PROF_BONUS = 3
PROF_BONUSES: dict[Prof, int] = {
    PROF.NONE: 0,
    PROF.HALF: BASE_PROF_BONUS // 2,
    PROF.FULL: BASE_PROF_BONUS,
    PROF.EXPERT: BASE_PROF_BONUS * 2,
}

Attr = Literal["Str", "Dex", "Con", "Int", "Wis", "Cha"]
ATTRS_LIST: list[Attr] = ["Str", "Dex", "Con", "Int", "Wis", "Cha"]

ALIGNMENTS: list[str] = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "True Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil",
]


class ATTRS:
    STR = "Str"
    DEX = "Dex"
    CON = "Con"
    INT = "Int"
    WIS = "Wis"
    CHA = "Cha"


Skill = Literal[
    "Acrobatics",
    "Animal Handling",
    "Arcana",
    "Athletics",
    "Deception",
    "History",
    "Insight",
    "Intimidation",
    "Investigation",
    "Medicine",
    "Nature",
    "Perception",
    "Performance",
    "Persuasion",
    "Religion",
    "Sleight of Hand",
    "Stealth",
    "Survival",
]
SKILLS: dict[Skill, Attr] = {
    "Acrobatics": "Dex",
    "Animal Handling": "Wis",
    "Arcana": "Int",
    "Athletics": "Str",
    "Deception": "Cha",
    "History": "Int",
    "Insight": "Wis",
    "Intimidation": "Cha",
    "Investigation": "Int",
    "Medicine": "Wis",
    "Nature": "Int",
    "Perception": "Wis",
    "Performance": "Cha",
    "Persuasion": "Cha",
    "Religion": "Int",
    "Sleight of Hand": "Dex",
    "Stealth": "Dex",
    "Survival": "Wis",
}

SKILL_ICONS: dict[Skill | Attr, str] = {
    # Saves
    "Str": "💪",
    "Dex": "🤸🏻‍♀️",
    "Con": "🛡️",
    "Int": "🧠",
    "Wis": "🧘",
    "Cha": "🗣️",
    # Skills
    "Athletics": "🏋️",
    "Acrobatics": "🤸🏻‍♀️",
    "Sleight of Hand": "👐",
    "Stealth": "🥷",
    "Arcana": "🔮",
    "History": "📜",
    "Investigation": "🔍",
    "Nature": "🌳",
    "Religion": "⛪",
    "Animal Handling": "🐴",
    "Insight": "🧠",
    "Medicine": "🩺",
    "Perception": "👀",
    "Survival": "🧭",
    "Deception": "🤥",
    "Intimidation": "😠",
    "Performance": "🎭",
    "Persuasion": "🗣️",
}


Class = Literal[
    "Artificer",
    "Blood Hunter",
    "Barbarian",
    "Bard",
    "Cleric",
    "Druid",
    "Fighter",
    "Monk",
    "Paladin",
    "Ranger",
    "Rogue",
    "Sorcerer",
    "Warlock",
    "Wizard",
]
CLASSES: dict[Class, list[str]] = {
    "Artificer": ["Alchemist", "Armorer", "Artillerist", "Battle Smith"],
    "Barbarian": [
        "Ancestral Guardian",
        "Battlerager",
        "Beast",
        "Berserker",
        "Giant",
        "Storm Herald",
        "Totem Warrior",
        "Wild Magic",
        "Zealot",
        "Booming Magnificence",
        "Hellfire",
        "Herald",
        "Thorns",
        "Juggernaut",
    ],
    "Bard": [
        "Creation",
        "Eloquence",
        "Glamour",
        "Lore",
        "Spirits",
        "Swords",
        "Valor",
        "Whispers",
        "Cat",
        "Echoes",
        "Investigation",
        "Shadows",
        "Tragedy",
    ],
    "Blood Hunter": ["Ghostslayer", "Lycan", "Mutant", "Profane soul"],
    "Cleric": [
        "Arcana",
        "Death",
        "Forge",
        "Grave",
        "Knowledge",
        "Life",
        "Light",
        "Nature",
        "Order",
        "Peace",
        "Tempest",
        "Trickery",
        "Twilight",
        "War",
        "Black Powder",
        "Hunt",
        "Mercy",
        "Portal",
        "Serpent",
        "Shadow",
        "Vermin",
        "Wind",
        "Blood",
        "Moon",
    ],
    "Druid": [
        "Dreams",
        "Land",
        "Moon",
        "Shepherd",
        "Spores",
        "Stars",
        "Wildfire",
        "Ash",
        "Bees",
        "Crystal",
        "Green",
        "Sand",
        "Shapeless",
        "Wind",
        "Blighted",
    ],
    "Fighter": [
        "Arcane Archer",
        "Banneret",
        "Battle Master",
        "Cavalier",
        "Champion",
        "Echo Knight",
        "Eldritch Knight",
        "Psi Warrior",
        "Rune Knight",
        "Samurai",
        "Chaplain",
        "Legionary",
        "Pugilist",
        "Radiant Pikeman",
        "Timeblade",
        "Tunnel Watcher",
        "Gunslinger",
    ],
    "Monk": [
        "Astral Self",
        "Ascendant Dragon",
        "Drunken Master",
        "Four Elements",
        "Kensei",
        "Long Death",
        "Mercy",
        "Open Hand",
        "Shadow",
        "Sun Soul",
        "Concordant Motion",
        "Dragon",
        "Humble Elephant",
        "Still Waters",
        "Tipsy Monkey",
        "Unerring Arrow",
        "Wild Cat",
        "Cobalt Soul",
    ],
    "Paladin": [
        "Ancients",
        "Conquest",
        "Crown",
        "Devotion",
        "Glory",
        "Redemption",
        "Vengeance",
        "Watchers",
        "Oathbreaker",
        "Elements",
        "Hearth",
        "Justice",
        "Plaguetouched",
        "Open Sea",
    ],
    "Ranger": [
        "Beast Master",
        "Fey Wanderer",
        "Gloom Stalker",
        "Horizon Walker",
        "Hunter",
        "Monster Slayer",
        "Swarmkeeper",
        "Drakewarden",
        "Beast Trainer",
        "Grove Warden",
        "Gunslinger",
        "Snake Speaker",
        "Spear of the Weald",
        "Wasteland Strider",
    ],
    "Rogue": [
        "Arcane Trickster",
        "Assassin",
        "Inquisitive",
        "Mastermind",
        "Phantom",
        "Scout",
        "Soulknife",
        "Swashbuckler",
        "Thief",
        "Cat Burglar",
        "Dawn Blade",
        "Sapper",
        "Smuggler",
        "Soulspy",
        "Underfoot",
    ],
    "Sorcerer": [
        "Aberrant Mind",
        "Clockwork Soul",
        "Draconic Bloodline",
        "Divine Soul",
        "Lunar Sorcery",
        "Shadow Magic",
        "Storm Sorcery",
        "Wild Magic",
        "Black Powder",
        "Cold-Blooded",
        "Hungering",
        "Resonant Body",
        "Rifthopper",
        "Spore",
        "Wastelander",
        "Runechild",
    ],
    "Warlock": [
        "Archfey",
        "Celestial",
        "Fathomless",
        "Fiend",
        "Genie",
        "Great Old One",
        "Hexblade",
        "Undead",
        "Undying",
        "Ancient Dragons",
        "Hunter in Darkness",
        "Old Wood",
        "Primordial",
    ],
    "Wizard": [
        "Abjuration",
        "Bladesinging",
        "Chronurgy",
        "Conjuration",
        "Divination",
        "Enchantment",
        "Evocation",
        "Graviturgy",
        "Illusion",
        "Necromancy",
        "Order of Scribes",
        "Transmutation",
        "War Magic",
        "Cantrip Adept",
        "Courser Mage",
        "Familiar Master",
        "Gravebinding",
        "Liminal",
        "Spellsmith",
        "Blood Magic",
    ],
}


GODS: list[str] = [
    "Aesis",
    "Zephyrion",
    "Vendicatore",
    "Effette",
    "Bacnofar",
    "Thassalion",
    "Thautrius",
    "Killadan",
    "Ytos",
    "Tanayo",
    "Azra",
    "Miteos",
    "Modrer",
    "Volcrax",
    "Nethris",
    "Siegreich",
    "Kushee",
    "Thoeus",
    "Tarum",
    "Morath Dagon",
    "Urukan",
    "Rases",
    "Runder",
    "Rodhia",
    "Mulekos",
]

RACES: dict[str, list[str]] = {
    "Aarakocra": [],
    "Aasimar": [],
    "Alseid": [],
    "Bugbear": [],
    "Catfolk": ["Pantheran", "Malkin"],
    "Centaur": [],
    "Changeling": [],
    "Deep Gnome": [],
    "Derro": ["Far-Touched", "Mutated", "Uncorrupted"],
    "Dhampir": [],
    "Dragonborn": ["Ravenite", "Chromatic", "Metallic", "Gem"],
    "Drow (ToH)": ["Delver", "Fever-Bit", "Purified"],
    "Duergar": [],
    "Dwarf": ["Spindrift", "Fireforge", "Mountain"],
    "Eladrin": [],
    "Elf": ["Drow", "Eladrin", "High", "Pallid", "Sea", "Shadar-Kai", "Wood", "Dunewalker", "Frostfell"],
    "Erina": [],
    "Fairy": [],
    "Genasi": ["Air", "Earth", "Fir", "Water"],
    "Giff": [],
    "Gith": ["Githyanki", "Githzerai"],
    "Gnome": ["Deep", "Svirfnebling", "Mark of Scribling", "Rock", "Shoal", "Wyrd"],
    "Goblin": [],
    "Goliath": [],
    "Hadozee": [],
    "Half-Elf": ["Aquatic", "Drow", "Moon", "Sun", "Wood"],
    "Half-Orc": [],
    "Halfling": [
        "Ghostwise",
        "Lightfoot",
        "Lotusden",
        "Stout",
        "Courtfolk",
        "Hinterfolk",
        "Riverfolk",
        "Urban",
        "Winterfolk",
    ],
    "Firbolg": [],
    "Harengon": [],
    "Hexblood": [],
    "Hobgoblin": [],
    "Human": ["Keldon", "Variant"],
    "Kalashtar": [],
    "Kender": [],
    "Kenku": [],
    "Kobold": [],
    "Leonin": [],
    "Lizardfolk": [],
    "Loxodon": [],
    "Minotaur": [],
    "Mushroomfolk": ["Acid cap", "Favored", "Morel"],
    "Orc": [],
    "Owlin": [],
    "Plasmoid": [],
    "Reborn": [],
    "Satarre": [],
    "Satyr": [],
    "Sea Elf": [],
    "Shadar-Kai": [],
}
