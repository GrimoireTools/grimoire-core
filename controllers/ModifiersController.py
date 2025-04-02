from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int

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


class ModifiersController(SheetsControllerBase[ModifiersRow]):
    def __init__(self):
        super().__init__(MODIFIERS_SHEET_ID, ModifiersRow)
