import json
from typing import (
    Generic,
    Self,
)

import gspread
from gspread.utils import ValueInputOption, ValueRenderOption
from gspread.worksheet import Worksheet
from loguru import logger
from grimoire_core.varenv import get_env

from grimoire_core.row import RowType
from grimoire_core.singleton import Singleton
from grimoire_core.utils import DataNotFoundError, column_to_num

credentials = json.loads(get_env("GOOGLE"), strict=False)


gc = gspread.auth.service_account_from_dict(credentials)
logger.debug("Google Sheets API authenticated successfully.")
logger.debug(f"Available spreadsheets: {[s['name'] for s in gc.list_spreadsheet_files()]}")

Col = int | str

Value = str | int | float

SHEET_KEY = get_env("SHEET_KEY")


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

    @classmethod
    def cached(cls) -> Self:
        """Returns the in-memory instance without hitting the API.

        Falls back to a full fetch if no instance exists yet.
        """
        try:
            return cls._instances[cls]
        except KeyError:
            raise RuntimeError(f"{cls.__name__} has not been instantiated yet.")

    def __init__(self, sheet_id: int, cls: type[RowType], doc_key: str = SHEET_KEY) -> None:
        """Initializes the class with the given sheet_id and row type."""
        logger.debug(f"Initializing {self.__class__.__name__} with sheet_id {sheet_id} and row type {cls.__name__}")
        self.row_type = cls
        self.sheet = gc.open_by_key(doc_key).get_worksheet_by_id(sheet_id)

    def fetch_data(self) -> None:
        """Fetches all data from the sheet. Called each time __init__() is called."""
        logger.debug("Fetching data from sheet...")
        self.DATA = self.sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)
        self._after_fetch()

    def _after_fetch(self) -> None:
        """Called after fetching data. Override this method to perform any additional processing."""
        pass

    def _convert_row(self, row: list[Value]) -> RowType:
        """Converts a list of values to a dataclass instance."""
        return self.row_type.from_list(row)

    def get_cell(self, row: int, col: Col) -> Value:
        """Returns a cell value. Row and col are 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = column_to_num(col)
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

    def get_all_rows(self, skip=1) -> list[RowType]:
        """Returns all rows as a list of dataclass instances. Remember that the first row is generally the header."""
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
        """Returns a column as a list of values. Col is 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = column_to_num(col)
        return [row[col] for row in self.DATA]

    def set_cell(self, row: int, col: Col, value: Value) -> None:
        """Sets a cell to a given value. Row and col are 0-indexed. Col can optionally be the letter identifier."""
        if isinstance(col, str):
            col = column_to_num(col)
        self.sheet.update_cell(row + 1, col + 1, value)
        self.DATA[row][col] = value

    def set_row(self, values: RowType, row: int = -1) -> None:
        """Sets a row to a given value."""
        row = row if row != -1 else values.get_index()
        if row == -1:
            raise ValueError("Row index not set and not present in values.")
        ranges = values._ranges(row)
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )
        self.DATA[row] = values.to_list()

    update_row = set_row

    def update_rows(self, values: list[RowType]) -> None:
        """Updates multiple rows at once."""
        ranges = []
        for value in values:
            ranges.extend(value._ranges(value.get_index()))
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )
        for value in values:
            self.DATA[value.get_index()] = value.to_list()

    def find_first_empty_row(self, col: Col, strict: bool = False) -> int:
        """Finds the first empty row in a given column. Strict makes it manually look for the first empty cell, insteda of giving the length of the column."""
        column = self.get_column(col)
        if strict:
            for i, cell in enumerate(column):
                if cell == "" or cell is None:
                    return i
            return len(column)
        return len(column)

    def col_letter(self, col_name: str) -> str:
        """Returns the column letter of a given column name."""
        return self.row_type.col_letter(col_name)

    def col_index(self, col_name: str) -> int:
        """Returns the 0-indexed column index of a given column name."""
        return self.row_type.col_index(col_name)

    def find_rows_with_values(self, values: dict[str, Value | list[Value]]) -> list[RowType]:
        """Finds all rows with values contained within the given values for each column.

        The values are a dictionary where the key is the column name and the value is the value or values to search for.
        The values can be a single value or a list of values. If a list is provided, the row will be returned if any of the values match.
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
        """Finds the index of the first row with a given discord_id in a given column."""
        id = str(discord_id)
        i_col = self.col_index(col_name)
        logger.debug(f"Searching for discord_id '{id}' in column {col_name} (index {i_col})")
        for i, row in enumerate(self.DATA):
            logger.debug(f"Checking row index {i}: {row[i_col]}")
            if str(row[i_col]) == id:
                logger.debug(f"Found discord_id '{id}' at row index {i}")
                return i
        raise DataNotFoundError("Row with given discord_id not found")

    def find_pj_row_index(self, discord_id: int) -> int:
        """Finds the index of row with the given discord_id."""
        # By default we assume that the discord id column has the name Discord_id
        return self.find_id_row_index(discord_id, "Discord_id")

    def insert_rows(self, values: list[RowType], row: int = -1) -> None:
        """Inserts multiple rows at the end of the sheet."""
        start_row = row if row != -1 else len(self.DATA)
        ranges = []
        for i, value in enumerate(values):
            ranges.extend(value._ranges(start_row + i))
        self.sheet.batch_update(
            ranges,
            value_input_option=ValueInputOption.user_entered,
        )
        for i, value in enumerate(values):
            target = start_row + i
            row_list = value.to_list()
            if target < len(self.DATA):
                self.DATA[target] = row_list
            else:
                self.DATA.append(row_list)

    def insert_row(self, value: RowType, row: int = -1):
        """Inserts a row at the end of the sheet."""
        return self.insert_rows([value], row)

    def delete_rows(self, start: int, end: int = -1) -> None:
        """Deletes a row from the sheet. 0-indexed."""
        if start == -1:
            raise ValueError("Row index for deletion cannot be negative.")
        start += 1
        end = end + 1 if end != -1 else start
        self.sheet.delete_rows(start, end)
        self.fetch_data()

    def delete_row(self, row: RowType) -> None:
        """Deletes a row from the sheet. 0-indexed."""
        self.delete_rows(row.get_index())

    def update_or_insert(self, row: RowType) -> None:
        """Updates a row if it already exists, otherwise inserts a new row."""
        if row.get_index() == -1:
            self.insert_row(row)
        else:
            self.update_row(row)

    def update_or_insert_batch(self, rows: list[RowType]) -> None:
        """Updates or inserts multiple rows."""
        insert_rows = [r for r in rows if r.get_index() == -1]
        update_rows = [r for r in rows if r.get_index() != -1]
        if insert_rows:
            self.insert_rows(insert_rows)
        if update_rows:
            self.update_rows(update_rows)
