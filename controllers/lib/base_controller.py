from typing import (
    Generic,
    Type,
)

import utils
from gspread.worksheet import Worksheet
from gspread.utils import ValueRenderOption, ValueInputOption
from .singleton import Singleton
from .row import RowType
import json
import gspread
from varenv import getVar
from loguru import logger

credentials = json.loads(getVar("GOOGLE"), strict=False)


gc = gspread.auth.service_account_from_dict(credentials)
Col = int | str

Value = str | int | float


class SheetsControllerBase(Generic[RowType], metaclass=Singleton):
    """
    Base class for all sheets controllers.

    Takes in a sheet_id and provides methods to interact with the sheet.

    All sheets interactions use 0-indexed rows and 0-indexed columns.

    """

    DATA: list[list[Value]]
    sheet: Worksheet
    row_type: Type[RowType]

    def __init__(self, sheet_id: int, cls: type[RowType]):
        self.row_type = cls
        self.sheet = gc.open("Megamarch").get_worksheet_by_id(sheet_id)
        # self.fetch_data()

    def fetch_data(self):
        """Fetches all data from the sheet. Called each time __init__() is called."""
        logger.debug("Fetching data from sheet...")
        self.DATA = self.sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)

    def _convert_row(self, row: list[Value]) -> RowType:
        """Converts a list of values to a dataclass instance."""
        return self.row_type.from_list(row)

    def get_cell(self, row: int, col: Col) -> Value:
        """Returns a cell value. Row and col are 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = utils.column_to_num(col)
        return self.DATA[row][col]

    def get_row_list(self, row: int) -> list[Value]:
        """Returns a row as a list of values. Row is 0-indexed."""
        return self.DATA[row]

    def get_row(self, row: int) -> RowType:
        """Returns a row as a dataclass instance. Row is 0-indexed. Remember that the first row is generally the header."""
        if row == -1:
            raise ValueError(f"Row index {row} not set and not present in values.")
        data_row = self._convert_row(self.DATA[row])
        data_row.set_index(row)
        return data_row

    def get_column(self, col: Col) -> list[Value]:
        """Returns a column as a list of values. Col is 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = utils.column_to_num(col)
        return [row[col] for row in self.DATA]

    def set_cell(self, row: int, col: Col, value: Value):
        """Sets a cell to a given value. Row and col are 0-indexed. Col can optinoally be the letter identifier."""
        if isinstance(col, str):
            col = utils.column_to_num(col)
        else:
            self.sheet.update_cell(row + 1, col + 1, value)

    def set_row(self, values: RowType, row: int = -1):
        """Sets a row to a given value."""
        row = row if row != -1 else values.get_index()
        if row == -1:
            raise ValueError("Row index not set and not present in values.")
        ranges = values._ranges(row)
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )

    def find_first_empty_row(self, col: Col) -> int:
        """Finds the first empty row in a given column."""
        column = self.get_column(col)
        return len(column) + 1

    def col_letter(self, col_name: str) -> str:
        """Returns the column letter of a given column name."""
        return self.row_type.col_letter(col_name)

    def col_index(self, col_name: str) -> int:
        """Returns the 0-indexed column index of a given column name."""
        return self.row_type.col_index(col_name)

    def find_id_row_index(self, discord_id: int, col_name: str) -> int:
        """Finds the index of the first row with a given discord_id in a given column."""
        id = str(discord_id)
        i_col = self.col_index(col_name)
        for i, row in enumerate(self.DATA):
            if row[i_col] == id:
                return i
        raise utils.CharacterNotFoundError

    def find_pj_row_index(self, discord_id: int) -> int:
        """Finds the index of row with the given discord_id."""
        # By default we assume that the discord id column has the name Discord_id
        return self.find_id_row_index(discord_id, "Discord_id")

    def insert_rows(self, values: list[RowType], row: int = -1):
        """Inserts multiple rows at the end of the sheet."""
        if row == -1:
            row = len(self.DATA)
        ranges = []
        for value in values:
            ranges.extend(value._ranges(row))
            row += 1
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )

    def delete_rows(self, start: int, end: int = -1):
        """Deletes a row from the sheet. 0-indexed."""
        if start == -1:
            raise ValueError("Row index for deletion cannot be negative.")
        start += 1
        end = end + 1 if end != -1 else start
        self.sheet.delete_rows(start, end)
        self.fetch_data()

    def delete_row(self, row: RowType):
        """Deletes a row from the sheet. 0-indexed."""
        self.delete_rows(row.get_index())
