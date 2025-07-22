"""Formulas Controller Module."""

from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row

FORMULA_SHEET_ID = 1160647453


class FormulaRow(Row):
    """Row for a formula entry."""

    Item_name: str
    Rarity: str
    Type: str
    Item_level: str
    Requirements: str


class FormulasController(SheetsControllerBase[FormulaRow]):
    """Controller for managing formulas."""

    def __init__(self) -> None:
        super().__init__(FORMULA_SHEET_ID, FormulaRow)
