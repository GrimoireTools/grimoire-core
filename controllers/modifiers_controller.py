from typing import Self, Tuple
from PF2eData import ABILITIES, Ability
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int
from controllers.lib.utils import DataNotFoundError, not_none

MODIFIERS_SHEET_ID = 41455486


class ModifiersRow(Row):
    PJ_name: str
    Discord_id: str
    STR: r_int
    DEX: r_int
    CON: r_int
    INT: r_int
    WIS: r_int
    CHA: r_int

    def __getitem__(self, key: str) -> int:
        key = key.upper()
        if key in self.__dict__:
            return not_none(getattr(self, key))
        raise KeyError(f"'{key}' is not a valid ability score")


class ModifiersController(SheetsControllerBase[ModifiersRow]):
    def __init__(self):
        super().__init__(MODIFIERS_SHEET_ID, ModifiersRow)

    def get_mods_row(self, user_id: int) -> ModifiersRow:
        """Gets the modifiers row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError(
                f"Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            ) from None

    def mods_row_exists(self, user_id: int) -> bool:
        """Checks if the modifiers row exists for a given user_id."""
        try:
            r = self.get_mods_row(user_id)
            return r is not None and True
        except DataNotFoundError:
            return False
