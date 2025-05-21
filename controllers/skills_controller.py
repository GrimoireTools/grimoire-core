from controllers.lib.prof_controller import ProficiencyControllerBase
from controllers.lib.row import Row
from controllers.lib.utils import not_none
from controllers.attributes_controller import AttributesRow
from system_data import SKILLS, Attr, Prof, Skill, PROF_BONUSES

SAVES_SHEET_ID = 625988153


class SkillRow(Row):
    PJ_name: str
    Discord_id: str
    Skill_name: Skill
    Proficiency: Prof
    Extra_bonus: int
    Bonus_description: str

    def mod_type(self) -> Attr:
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

    def modifiers_description(self, mods: AttributesRow, additional: int = 0) -> str:
        """
        Devuelve el modificador y la descripción del bono
        """
        mod_type = self.mod_type()
        extra = f"[Extra: {self.Extra_bonus:+}]" if self.Extra_bonus != 0 else ""
        more = f"[Other: {additional:+}]" if additional != "" else ""
        return f"[{mod_type}: {mods[mod_type]:+}][{self.Proficiency}: {self.prof_bonus():+}]{extra}{more}"

    def total_bonus(self, mods: AttributesRow, additional: int = 0) -> int:
        """
        Devuelve el modificador total
        """
        return (mods[self.mod_type()] - 10) // 2 + self.prof_bonus() + not_none(self.Extra_bonus) + additional


def skill_mod_type(skill: str | SkillRow):
    """
    Devuelve el tipo de modificador
    """

    if isinstance(skill, SkillRow):
        skill = skill.Skill_name
    if skill in SKILLS:
        return SKILLS[skill]
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
