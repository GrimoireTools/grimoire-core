from system_data import PROF_BONUSES
from controllers.lib.prof_controller import ProficiencyControllerBase
from controllers.lib.row import Row

SAVES_SHEET_ID = 1756443107


class SaveRow(Row):
    PJ_name: str
    Discord_id: str
    Save_name: str
    Proficiency: str
    Extra_bonus: int
    Bonus_description: str

    def mod_type(self) -> str:
        return self.Save_name

    def prof_bonus(self) -> int:
        """
        Devuelve el bono de competencia
        """
        if self.Proficiency in PROF_BONUSES:
            return PROF_BONUSES[self.Proficiency]
        else:
            raise ValueError(
                f"'{self.Proficiency}' is not a valid proficiency type")


class SavesController(ProficiencyControllerBase[SaveRow]):
    def __init__(self):
        super().__init__(SAVES_SHEET_ID, SaveRow, "Save_name")
