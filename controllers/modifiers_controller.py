"""Modifiers Controller Module."""

from PF2eData import Ability
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row
from controllers.lib.utils import DataNotFoundError, not_none

MODIFIERS_SHEET_ID = 41455486


class ModifiersRow(Row):
    """Row for a modifiers entry."""

    PJ_name: str
    Discord_id: str
    STR: int
    DEX: int
    CON: int
    INT: int
    WIS: int
    CHA: int

    def __getitem__(self, ability: Ability) -> int:
        """Get the modifier for a given ability."""
        key = ability.upper()
        if key in self.__dict__:
            return not_none(getattr(self, key))
        raise KeyError(f"'{ability}' is not a valid ability modifer")


class ModifiersController(SheetsControllerBase[ModifiersRow]):
    """Controller for managing modifiers."""

    def __init__(self) -> None:
        super().__init__(MODIFIERS_SHEET_ID, ModifiersRow)

    def get_mods_row(self, user_id: int) -> ModifiersRow:
        """Get the modifiers row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            ) from None

    def mods_row_exists(self, user_id: int) -> bool:
        """Check if the modifiers row exists for a given user_id."""
        try:
            r = self.get_mods_row(user_id)
            return r is not None and True
        except DataNotFoundError:
            return False
