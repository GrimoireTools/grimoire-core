from PF2eData import Ability, Prof, Save
from controllers.lib.prof_controller import ProficiencyControllerBase
from controllers.lib.row import Row
from level_bonuses import PROF_BONUSES

SAVES_SHEET_ID = 1756443107


class SaveRow(Row):
    PJ_name: str
    Discord_id: str
    Save_name: Save
    Proficiency: Prof
    Extra_bonus: int
    Bonus_description: str

    def mod_type(self) -> Ability:
        return save_mod_type(self.Save_name)

    def prof_bonus(self) -> int:
        """Devuelve el bono de competencia."""
        if self.Proficiency in PROF_BONUSES:
            return PROF_BONUSES[self.Proficiency](self.Discord_id)
        else:
            raise ValueError(f"'{self.Proficiency}' is not a valid proficiency type")


class SavesController(ProficiencyControllerBase[SaveRow]):
    def __init__(self) -> None:
        super().__init__(SAVES_SHEET_ID, SaveRow, "Save_name")


def save_mod_type(save: Save | SaveRow) -> Ability:
    """Devuelve el tipo de modificador."""
    mods: dict[Save, Ability] = {
        "Fortitude": "Con",
        "Reflex": "Dex",
        "Will": "Wis",
    }
    if isinstance(save, SaveRow):
        save = save.Save_name
    if save in mods:
        return mods[save]
    else:
        raise ValueError(f"'{save}' is not a valid save name")
