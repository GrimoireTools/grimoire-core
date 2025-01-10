from dataclasses import dataclass
import json
from typing import Any, Generic, TypeVar, Union, get_args
import gspread

import utils
from gspread.worksheet import Worksheet
from gspread.utils import ValueRenderOption

# from varenv import getVar

# credentials = json.loads(getVar("GOOGLE"), strict=False)


# gc = gspread.auth.service_account_from_dict(credentials)


SKIP_CELL = None


def skipify(value: Any) -> Any:
    if value == SKIP_CELL:
        return SKIP_CELL
    if value is None:
        return SKIP_CELL
    if isinstance(value, list):
        return [skipify(v) for v in value]
    if isinstance(value, dict):
        return {k: skipify(v) for k, v in value.items()}
    else:
        return value


class Skip:
    def __init__(self, value: Any = None):
        return skipify(value)


SKIP_CELL = Skip()


def rangeify(row: int, start: int, end: int):
    return f"{utils.num_to_column(start + 1)}{row}:{utils.num_to_column(end + 1)}{row}"


Col = int | str

Value = str | int | float | bool | Skip


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SheetRow:
    """
    Base class for all rows in the sheets.
    Given it's defined list of annotations, it will cast the values to the correct types.

    The Skip type and SKIP_CELL value can be used for cells that should not be updated in the sheet.
    Example:
    ```
    class PJRow(SheetRow):
        name: str
        lvl: int
        gp: int | Skip
    ```


    """

    def __init__(self, row: list[Value] | dict[str, Value], partial: bool = False):
        """Given a list of Excel values, fills the class attributes."""
        self._values = {}
        self._rowNames = list(self.__annotations__.keys())
        self._partial = partial
        if self._partial:
            # Si es parcial, se añade Skip a todas las anotaciones
            for key in self.__annotations__:
                if not isinstance(self.__annotations__[key], type(Union)):
                    self.__annotations__[key] = Union[self.__annotations__[key], Skip]
                else:
                    self.__annotations__[key] = Union[self.__annotations__[key], Skip]
        if isinstance(row, dict):
            self._from_dict(row)
        else:
            self._from_row(row)

    def _from_row(self, row: list[Value]):
        """Given a list of values, fills the class attributes."""
        if len(row) != len(self.__annotations__):
            raise ValueError(
                f"{self.__class__.__name__}: Row length ({len(row)}) does not match annotations length ({len(self.__annotations__)})"
            )
        for value, key in zip(row, self.__annotations__):
            self._values[key] = self._cast_value(key, value)

    def _to_row(self) -> list[Value]:
        """Returns a list of values with the current values of the class"""
        return [self._values[key] for key in self.__annotations__ if key in self._values]

    def _from_dict(self, row: dict[str, Value]):
        """Given a dict of values, fills the class attributes."""
        if not self._partial and not all(key in row for key in self.__annotations__):
            raise ValueError(
                f"{self.__class__.__name__}: Row does not contain all the required keys: {self.__annotations__.keys()}"
            )
        for key in self.__annotations__:
            if key in row:
                self._values[key] = self._cast_value(key, row[key])
            elif self._partial:
                self._values[key] = Skip
            else:
                raise ValueError(f"{self.__class__.__name__}: Row does not contain key {key}")

    def _to_dict(self) -> dict[str, Value]:
        """Returns a dict of values with the current values of the class"""
        return self._values

    def _cast(self, value: Value, val_type: type) -> Value:
        """Casts a value to a given type, with a speicla case for Skip values."""
        if val_type == Skip:
            return SKIP_CELL
        else:
            return val_type(value)

    def _cast_value(self, name: str, value: Value) -> Value:
        """Casts a value to the type defined in the annotations."""
        _type = self.__annotations__[name]
        if isinstance(_type, type(Union)):
            _types = get_args(_type)
            for _typ in _types:
                try:
                    return self._cast(value, _typ)
                except ValueError:
                    pass
            raise ValueError(f"Value {value} could not be casted to any of the types in the Union: {_types}")
        else:
            return self._cast(value, _type)

    def _range(self, row) -> tuple[list[str], list[list[Value]]]:
        values = self._to_row()
        col_start = 0
        col_end = 0
        in_range = False
        ranges = []
        val_ranges = []
        curr_range = []
        for i, val in enumerate(values):
            if val == SKIP_CELL:
                if in_range:
                    ranges.append(rangeify(row, col_start, col_end))
                    val_ranges.append(curr_range)
                    curr_range = []
                    in_range = False
            else:
                if not in_range:
                    col_start = i
                    in_range = True
                col_end = i
                curr_range.append(val)
        ranges.append(rangeify(row, col_start, col_end))
        val_ranges.append(curr_range)
        return ranges, val_ranges

    def __setattr__(self, name: str, value: Value):
        """Overrides the setter to cast values to the types defined in the annotations."""
        if name in self.__annotations__:
            self._values[name] = self._cast_value(name, value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Value:
        """Overrides the getter to cast values to the types defined in the annotations."""
        if name in self._values:
            return self._cast_value(name, self._values[name])
        else:
            return super().__getattribute__(name)


class PJRow(SheetRow):
    a: int
    b: int
    c: int | Skip
    d: str


a = PJRow([1, 2, 3, 1])

print(a._range(1))


# a.c = SKIP_CELL
# print(a.c == SKIP_CELL)
# print(a.b)

t1 = int | str
t2 = t1 | float
print(get_args(t2))

RowType = TypeVar("RowType", bound=SheetRow)


# class SheetsControllerBase(Generic[RowType], metaclass=Singleton):
#     """
#     Base class for all sheets controllers.

#     Takes in a sheet_id and provides methods to interact with the sheet.

#     All sheets interactions use 0-indexed rows and 0-indexed columns.

#     """

#     DATA: list[list[Value]]
#     sheet: Worksheet

#     def __init__(self, sheet_id: int, cls: type[RowType]):
#         self.row_type = cls
#         self.sheet = gc.open("Megamarch").get_worksheet_by_id(sheet_id)

#     def fetch_data(self):
#         self.DATA = self.sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)

#     def _convert_row(self, row: list[Value]) -> RowType:
#         return self.row_type(row)

#     def get_cell(self, row: int, col: Col) -> Value:
#         if isinstance(col, str):
#             col = utils.column_to_num(col)
#         return self.DATA[row][col]

#     def get_row(self, row: int) -> list[Value]:
#         return self.DATA[row]

#     def get_column(self, col: Col) -> list[Value]:
#         if isinstance(col, str):
#             col = utils.column_to_num(col)
#         return [row[col] for row in self.DATA]

#     def set_cell(self, row: int, col: Col, value: Value):
#         if value == SKIP_CELL:
#             return
#         if isinstance(col, str):
#             col = utils.column_to_num(col)
#         self.sheet.update_cell(row, col, value)

#     def set_row(self, row: int, values: RowType):

#         self.sheet.batch_update()

#     def find_first_empty_row(self, col: Col) -> int:
#         column = self.get_column(col)
#         return len(column) + 1
