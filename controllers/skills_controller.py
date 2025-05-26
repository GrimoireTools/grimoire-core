from typing import Tuple
from PF2eData import SKILLS, Ability, Prof, Skill
from controllers.lib.prof_controller import ProficiencyControllerBase
from controllers.lib.row import Row, r_int
from controllers.lib.singleton import Singleton
from controllers.lib.utils import not_none
from controllers.modifiers_controller import ModifiersRow
from level_bonuses import PROF_BONUSES

SAVES_SHEET_ID = 738258837


class SkillRow(Row):
    PJ_name: str
    Discord_id: str
    Skill_name: str | Skill
    Proficiency: Prof
    Extra_bonus: int
    Bonus_description: str

    def mod_type(self) -> Ability:
        return skill_mod_type(self.Skill_name)

    def is_lore(self) -> bool:
        return self.Skill_name.lower().startswith("lore")

    def prof_bonus(self) -> int:
        """
        Devuelve el bono de competencia
        """
        if self.Proficiency in PROF_BONUSES:
            return PROF_BONUSES[self.Proficiency](self.Discord_id)
        else:
            raise ValueError(f"'{self.Proficiency}' is not a valid proficiency type")

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


def skill_mod_type(skill: Skill | SkillRow | str) -> Ability:
    """
    Devuelve el tipo de modificador
    """

    if isinstance(skill, SkillRow):
        skill = skill.Skill_name
    if skill in SKILLS:
        return SKILLS[skill]
    elif skill.lower().startswith("lore"):
        return "Int"
    else:
        raise ValueError(f"'{skill}' is not a valid skill name")


class SkillsController(ProficiencyControllerBase[SkillRow]):

    def __init__(self):
        super().__init__(SAVES_SHEET_ID, SkillRow, "Skill_name")

    def get_skill_or_untrained(self, user_id: int, skill_name: Skill | str) -> SkillRow:
        """
        Returns the skill name and proficiency for a given user_id and skill_name.
        If the skill is not found, returns an anonymous untrained skill row.
        """
        return self.get_prof_row(user_id, skill_name) or SkillRow(
            PJ_name="Anonymous",
            Discord_id=user_id,
            Skill_name=skill_name,
            Proficiency="Untrained",
            Extra_bonus=0,
            Bonus_description="",
        )


class LoreSubnames(metaclass=Singleton):
    _LORE_SUBNAMES: dict[str, list[str]]  # user_id, Lore subnames

    def udpate_lore_subnames(self) -> None:
        """Updates the lore subnames in the proficiency sheet."""

        user_col = SkillRow.col_index("Discord_id")
        skill_col = SkillRow.col_index("Skill_name")

        user_lores = {}

        sh_skills = SkillsController()

        for row in sh_skills.DATA:
            user_id = str(row[user_col])
            skill_name = str(row[skill_col])
            if not skill_name.lower().startswith("lore"):
                continue

            if user_id in user_lores:
                user_lores[user_id].append(skill_name[6:-1])
            else:
                user_lores[user_id] = [skill_name[6:-1]]
        # Se asume que todos los lores están en formato "Lore (subname)"
        self._LORE_SUBNAMES = user_lores

    def user_lore_subnames(self, user_id: int) -> list[str]:
        """Returns the lore subnames for a given user_id."""
        if self._LORE_SUBNAMES is None:
            self.udpate_lore_subnames()
        return self._LORE_SUBNAMES.get(str(user_id), [])

    def all_lore_subnames(self) -> list[str]:
        """Returns all lore subnames."""
        # Magia negra: flattenea la lista de listas y elimina duplicados
        return list(set([val for values in self._LORE_SUBNAMES.values() for val in values]))
