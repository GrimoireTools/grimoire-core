"""Base controller module for Google Sheets interaction.

Provides a generic base class for interacting with Google Sheets using gspread.
Includes methods for fetching, updating, inserting, and deleting rows and cells.
Intended for subclassing with specific row dataclasses.

Important Classes:
    - SheetsControllerBase: Base class for sheet controllers.
"""

from typing import (
    Generic,
)
from .utils import DataNotFoundError, column_to_num
from gspread.worksheet import Worksheet
from gspread.utils import ValueRenderOption, ValueInputOption
from .singleton import Singleton
from .row import RowType
import json
import gspread
from varenv import get_var
from loguru import logger

credentials = json.loads(get_var("GOOGLE"), strict=False)


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
    row_type: type[RowType]
    marker_col: int = 1  # Columna que se revisa para saber si la fila existe

    def __init__(self, sheet_id: int, cls: type[RowType], doc: str = "Megamarch") -> None:
        """Initialize the class with the given sheet_id and row type."""
        logger.debug(f"Initializing {self.__class__.__name__} with sheet_id {sheet_id} and row type {cls.__name__}")
        self.row_type = cls
        self.sheet = gc.open(doc).get_worksheet_by_id(sheet_id)

    def fetch_data(self) -> None:
        """Fetch all data from the sheet. Called each time __init__() is called."""
        logger.debug("Fetching data from sheet...")
        self.DATA = self.sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)
        self._after_fetch()

    def _after_fetch(self) -> None:
        """Override this method to perform any additional processing after fetching data."""
        pass

    def _convert_row(self, row: list[Value]) -> RowType:
        """Convert a list of values to a dataclass instance."""
        return self.row_type.from_list(row)

    def get_cell(self, row: int, col: Col) -> Value:
        """Return a cell value. Row and col are 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = column_to_num(col)
        return self.DATA[row][col]

    def get_row_list(self, row: int) -> list[Value]:
        """Return a row as a list of values. Row is 0-indexed."""
        return self.DATA[row]

    def get_row(self, row: int) -> RowType:
        """Return a row as a dataclass instance.

        Row is 0-indexed. Remember that the first row is generally the header.
        """
        if row == -1:
            raise ValueError(f"Row index {row} not set and not present in values.")
        data_row = self._convert_row(self.DATA[row])
        data_row.set_index(row)
        return data_row

    def get_all_rows(self, skip: int = 1) -> list[RowType]:
        """Return all rows as a list of dataclass instances. Remember that the first row is generally the header."""
        rows = []
        data = self.DATA[skip:]
        for i, row in enumerate(data):
            if row[self.marker_col] == "":
                # Skip empty rows
                continue
            data_row = self._convert_row(row)
            data_row.set_index(i + 1)
            rows.append(data_row)
        return rows

    def get_column(self, col: Col) -> list[Value]:
        """Return a column as a list of values. Col is 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = column_to_num(col)
        return [row[col] for row in self.DATA]

    def set_cell(self, row: int, col: Col, value: Value) -> None:
        """Set a cell to a given value. Row and col are 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = column_to_num(col)
        else:
            self.sheet.update_cell(row + 1, col + 1, value)

    def set_row(self, values: RowType, row: int = -1) -> None:
        """Set a row to a given value."""
        row = row if row != -1 else values.get_index()
        if row == -1:
            raise ValueError("Row index not set and not present in values.")
        ranges = values._ranges(row)
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )

    update_row = set_row

    def update_rows(self, values: list[RowType]) -> None:
        """Update multiple rows at once."""
        ranges = []
        for value in values:
            ranges.extend(value._ranges(value.get_index()))
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )

    def find_first_empty_row(self, col: Col, strict: bool = False) -> int:
        """Find the first empty row in a given column.

        Strict makes it manually look for the first empty cell, instead of giving the length of the column.
        """
        column = self.get_column(col)
        if strict:
            for i, cell in enumerate(column):
                if cell == "" or cell is None:
                    return i
            return len(column) + 1
        return len(column) + 1

    def col_letter(self, col_name: str) -> str:
        """Return the column letter of a given column name."""
        return self.row_type.col_letter(col_name)

    def col_index(self, col_name: str) -> int:
        """Return the 0-indexed column index of a given column name."""
        return self.row_type.col_index(col_name)

    def find_rows_with_values(self, values: dict[str, Value | list[Value]]) -> list[RowType]:
        """Find all rows with values contained within the given values for each column.

        The values are a dictionary where the key is the column name and the value is the value or values to search for.
        The values can be a single value or a list of values.
        If a list is provided, the row will be returned if any of the values match.
        """
        rows = []
        for i, row in enumerate(self.DATA):
            meets_conditions = True
            for col_name, value_s in values.items():
                # Check if the column contains the value
                col_index = self.col_index(col_name)
                cell_value = row[col_index]
                if isinstance(value_s, list):
                    meets_conditions = meets_conditions and cell_value in value_s
                else:
                    meets_conditions = meets_conditions and cell_value == value_s
                if not meets_conditions:
                    break
            if meets_conditions:
                rows.append(self.get_row(i))
        return rows

    def find_id_row_index(self, discord_id: int, col_name: str) -> int:
        """Find the index of the first row with a given discord_id in a given column."""
        id = str(discord_id)
        i_col = self.col_index(col_name)
        for i, row in enumerate(self.DATA):
            if str(row[i_col]) == id:
                return i
        raise DataNotFoundError("Row with given discord_id not found")

    def find_pj_row_index(self, discord_id: int) -> int:
        """Find the index of row with the given discord_id."""
        # By default we assume that the discord id column has the name Discord_id
        return self.find_id_row_index(discord_id, "Discord_id")

    def insert_rows(self, values: list[RowType], row: int = -1) -> None:
        """Insert multiple rows at the end of the sheet."""
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

    def insert_row(self, value: RowType, row: int = -1) -> None:
        """Insert a row at the end of the sheet."""
        return self.insert_rows([value], row)

    def delete_rows(self, start: int, end: int = -1) -> None:
        """Delete rows from the sheet. 0-indexed."""
        if start == -1:
            raise ValueError("Row index for deletion cannot be negative.")
        start += 1
        end = end + 1 if end != -1 else start
        self.sheet.delete_rows(start, end)
        self.fetch_data()

    def delete_row(self, row: RowType) -> None:
        """Delete a row from the sheet. 0-indexed."""
        self.delete_rows(row.get_index())

    def update_or_insert(self, row: RowType) -> None:
        """Update a row if it already exists, otherwise insert a new row."""
        if row.get_index() == -1:
            self.insert_row(row)
        else:
            self.update_row(row)

    def update_or_insert_batch(self, rows: list[RowType]) -> None:
        """Update or insert multiple rows."""
        insert_rows = [r for r in rows if r.get_index() == -1]
        update_rows = [r for r in rows if r.get_index() != -1]
        if insert_rows:
            self.insert_rows(insert_rows)
        if update_rows:
            self.update_rows(update_rows)
