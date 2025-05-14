from typing import Optional
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int

SALARY_SHEET_ID = 1681819644


LEVEL_GLOBAL = 10


class SalaryRow(Row):
    Name: str
    Discord_id: str
    Turn: int
    Info: str


class SalaryController(SheetsControllerBase[SalaryRow]):
    def __init__(self):
        super().__init__(SALARY_SHEET_ID, SalaryRow)

    def get_user_logs(user_id: int) -> list[SalaryRow]:
        pass
