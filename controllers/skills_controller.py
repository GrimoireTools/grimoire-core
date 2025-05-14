from controllers.lib.prof_controller import ProficiencyControllerBase
from controllers.lib.row import Row
from controllers.lib.singleton import Singleton
from controllers.lib.utils import not_none, PROF_BONUSES
from controllers.modifiers_controller import ModifiersRow
from system_data import Attr
SAVES_SHEET_ID = 738258837


class SkillRow(Row):
    PJ_name: str
    Discord_id: str
    Skill_name: str
    Proficiency: str
    Extra_bonus: int
    Bonus_description: str

    def mod_type(self) -> str:
        return skill_mod_type(self.Skill_name)

    def prof_bonus(self) -> int:
        """
        Devuelve el bono de competencia
        """
        if self.Proficiency in PROF_BONUSES:
            return PROF_BONUSES[self.Proficiency]
        else:
            raise ValueError(
                f"'{self.Proficiency}' is not a valid proficiency type")

    def modifiers_description(self, mods: ModifiersRow, additional: int = 0) -> str:
        """
        Devuelve el modificador y la descripción del bono
        """
        mod_type = self.mod_type()
        extra = f"[Extra: {self.Extra_bonus:+}]" if self.Extra_bonus != 0 else ""
        more = f"[Other: {additional:+}]" if additional != "" else ""
        return f"[{mod_type}: {mods[mod_type]:+}][{self.Proficiency}: {self.prof_bonus():+}]{extra}{more}"

    def total_bonus(self, mods: ModifiersRow, additional: int = 0) -> int:
        """
        Devuelve el modificador total
        """
        return mods[self.mod_type()] + self.prof_bonus() + not_none(self.Extra_bonus) + additional


def skill_mod_type(skill: str | SkillRow):
    """
    Devuelve el tipo de modificador
    """
    mods: dict[str, Attr] = {
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
    if isinstance(skill, SkillRow):
        skill = skill.Skill_name
    if skill in mods:
        return mods[skill]
    else:
        raise ValueError(f"'{skill}' is not a valid skill name")


class SkillsController(ProficiencyControllerBase[SkillRow]):

    def __init__(self):
        super().__init__(SAVES_SHEET_ID, SkillRow, "Skill_name")

    def get_skill_or_untrained(self, user_id: int, skill_name: str) -> SkillRow:
        """
        Returns the skill name and proficiency for a given user_id and skill_name.
        If the skill is not found, returns an anonymous untrained skill row.
        """
        return self.get_prof_row(user_id, skill_name) or SkillRow(
            PJ_name="Anonymous",
            Discord_id=user_id,
            Skill_name=skill_name,
            Proficiency="None",
            Extra_bonus=0,
            Bonus_description="",
        )
