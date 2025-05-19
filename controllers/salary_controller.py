from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row

SALARY_SHEET_ID = 1872922705


class SalaryRow(Row):
    Start_level: int
    End_level: int
    Base_salary: int
    Salary: float

    def contains(self, val: int):
        return self.Start_level <= val and val <= self.End_level


class SalaryController(SheetsControllerBase[SalaryRow]):
    def __init__(self):
        super().__init__(SALARY_SHEET_ID, SalaryRow)

    def get_salary(self, turn: int) -> float:
        """
        Get the salary for a given level.
        :param level: The level of the character.
        :return: The salary for the given level.
        """
        if turn < 1:
            raise ValueError("Turn must be 1 or higher")

        rows = self.get_all_rows()

        for r in rows:
            if r.contains(turn):
                return r.Salary
        return 0

    def get_downtime(self) -> int:
        """
        Get the downtime awarded to characters per turn.
        """
        return 15
