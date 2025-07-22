from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row

FORMULA_SHEET_ID = 1160647453


class FormulaRow(Row):
    Item_name: str
    Rarity: str
    Type: str
    Item_level: str
    Requirements: str


class FormulasController(SheetsControllerBase[FormulaRow]):
    def __init__(self) -> None:
        super().__init__(FORMULA_SHEET_ID, FormulaRow)
