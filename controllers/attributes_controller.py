from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row
from controllers.lib.utils import DataNotFoundError, not_none

MODIFIERS_SHEET_ID = 478854727


def mod_bonus(score: int) -> int:
    """
    Devuelve el bono de modificador
    """
    return (score - 10) // 2


class AttributesRow(Row):
    PJ_name: str
    Discord_id: str
    STR: int
    DEX: int
    CON: int
    INT: int
    WIS: int
    CHA: int

    def __getitem__(self, key: str) -> int:
        key = key.upper()
        if key in self.__dict__:
            return not_none(getattr(self, key))
        raise KeyError(f"'{key}' is not a valid ability score")

    def pretty(self) -> str:
        """Returns a pretty string representation of the row."""
        return (
            f"- Fuerza: **{mod_bonus(self.STR):+}** ({self.STR:+})\n"
            f"- Destreza: **{mod_bonus(self.DEX):+}** ({self.DEX:+})\n"
            f"- Constitución: **{mod_bonus(self.CON):+}** ({self.CON:+})\n"
            f"- Inteligencia: **{mod_bonus(self.INT):+}** ({self.INT:+})\n"
            f"- Sabiduría: **{mod_bonus(self.WIS):+}** ({self.WIS:+})\n"
            f"- Carisma: **{mod_bonus(self.CHA):+}** ({self.CHA:+})\n"
        )


class AttributesController(SheetsControllerBase[AttributesRow]):
    def __init__(self):
        super().__init__(MODIFIERS_SHEET_ID, AttributesRow)

    def get_mods_row(self, user_id: int) -> AttributesRow:
        """Gets the modifiers row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError(
                f"Tu personaje no tiene modificadores de habilidad definidos. Definelos con /atributos."
            ) from None

    def mods_row_exists(self, user_id: int) -> bool:
        """Checks if the modifiers row exists for a given user_id."""
        try:
            r = self.get_mods_row(user_id)
            return r is not None and True
        except DataNotFoundError:
            return False
