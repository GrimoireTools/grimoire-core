from typing import Optional
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int

SALARY_SHEET_ID = 1681819644


LEVEL_GLOBAL = 10


class SalaryRow(Row):
    Level: int
    Base_salary: float
    Salary: float
    Others: str


class SalaryController(SheetsControllerBase[SalaryRow]):
    def __init__(self):
        super().__init__(SALARY_SHEET_ID, SalaryRow)

    def get_salary(self, level: int) -> float:
        """
        Get the salary for a given level.
        :param level: The level of the character.
        :return: The salary for the given level.
        """
        if level < 1 or level > 20:
            raise ValueError("Level must be between 1 and 20.")

        row = self.get_row(level)
        if row is None:
            return 0
        return row.Salary

    def get_salary_multiplier(self) -> float:
        """
        Get the salary multiplier.
        :return: The salary multiplier.
        """
        row = self.get_row(1)
        return float(row.Others)

    def get_downtime(self) -> int:
        """
        Get the downtime awarded to characters per turn.
        """
        row = self.get_row(3)
        return int(row.Others)

    def get_global_level(self) -> int:
        """
        Get the global level.
        """
        row = self.get_row(6)
        return int(row.Others)

    def set_global_level(self, level: int) -> None:
        """
        Set the global level.
        """
        row = self.get_row(6)
        row.Others = str(level)
        self.set_row(row, 6)


def update_level_global(new_value: Optional[int] = None) -> None:
    global LEVEL_GLOBAL
    sh = SalaryController()
    if new_value is None:
        LEVEL_GLOBAL = sh.get_global_level()
    else:
        sh.set_global_level(new_value)
        LEVEL_GLOBAL = new_value


def get_level_global() -> int:
    global LEVEL_GLOBAL
    return LEVEL_GLOBAL
