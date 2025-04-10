from PF2eData import PROF_BONUSES
from controllers.lib.prof_controller import ProficiencyControllerBase
from controllers.lib.row import Row, r_int

SAVES_SHEET_ID = 1756443107


class SaveRow(Row):
    PJ_name: str
    Discord_id: str
    Save_name: str
    Proficiency: str
    Extra_bonus: r_int
    Bonus_description: str

    def mod_type(self) -> str:
        return save_mod_type(self.Save_name)

    def prof_bonus(self) -> int:
        """
        Devuelve el bono de competencia
        """
        if self.Proficiency in PROF_BONUSES:
            return PROF_BONUSES[self.Proficiency]
        else:
            raise ValueError(f"'{self.Proficiency}' is not a valid proficiency type")


class SavesController(ProficiencyControllerBase[SaveRow]):
    def __init__(self):
        super().__init__(SAVES_SHEET_ID, SaveRow, "Save_name")


def save_mod_type(skill: str | SaveRow):
    """
    Devuelve el tipo de modificador
    """
    mods = {
        "Fortitude": "Con",
        "Reflex": "Dex",
        "Will": "Wis",
    }
    if isinstance(skill, SaveRow):
        skill = skill.Save_name
    if skill in mods:
        return mods[skill]
    else:
        raise ValueError(f"'{skill}' is not a valid skill name")
