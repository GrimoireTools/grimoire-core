from dataclasses import MISSING, dataclass, field, fields
from functools import wraps
import inspect
import json
from types import UnionType
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    Self,
    Type,
    TypeVar,
    TypedDict,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
import gspread

import utils
from gspread.worksheet import Worksheet
from gspread.utils import ValueRenderOption, ValueInputOption
from icecream import ic
from abc import ABC

# from varenv import getVar

# credentials = json.loads(getVar("GOOGLE"), strict=False)


# gc = gspread.auth.service_account_from_dict(credentials)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        instance = cls._instances[cls]
        if hasattr(instance, "fetch_data"):
            instance.fetch_data()
        return instance


# class Skip(metaclass=Singleton):

#     @staticmethod
#     def skipify(value: Any) -> Any:
#         if isinstance(value, list):
#             return [Skip.skipify(v) for v in value]
#         if isinstance(value, dict):
#             return {k: Skip.skipify(v) for k, v in value.items()}
#         if value is None or isinstance(value, Skip):
#             return Skip()
#         else:
#             return value

#     def __eq__(self, other):
#         return isinstance(other, Skip)

#     def __mul__(self, other):
#         if isinstance(other, (int, float, Skip)):
#             return Skip()
#         return NotImplemented

#     def __rmul__(self, other):
#         return self.__mul__(other)

#     def __add__(self, other):
#         if isinstance(other, (int, float, Skip)):
#             return Skip()
#         return NotImplemented

#     def __radd__(self, other):
#         return self.__add__(other)

#     def __sub__(self, other):
#         if isinstance(other, (int, float, Skip)):
#             return Skip()
#         return NotImplemented

#     def __rsub__(self, other):
#         return self.__sub__(other)

#     def __truediv__(self, other):
#         if isinstance(other, (int, float, Skip)):
#             return Skip()
#         return NotImplemented

#     def __rtruediv__(self, other):
#         return self.__truediv__(other)

#     def __contains__(self, item):
#         return False

#     def __len__(self):
#         return 0

#     def __getitem__(self, key):
#         return Skip()

#     def __iter__(self):
#         return iter([])

#     def __reversed__(self):
#         return iter([])

#     def __str__(self):
#         return "SKIP_CELL"

#     def __repr__(self):
#         return "SKIP_CELL"

#     def __format__(self, format_spec):
#         return "SKIP_CELL"

#     def __hash__(self):
#         return hash("SKIP_CELL")

#     def __lt__(self, other):
#         if isinstance(other, Skip):
#             return False
#         raise TypeError("Cannot compare Skip with non-Skip type")

#     def __le__(self, other):
#         if isinstance(other, Skip):
#             return True
#         raise TypeError("Cannot compare Skip with non-Skip type")

#     def __gt__(self, other):
#         if isinstance(other, Skip):
#             return False
#         raise TypeError("Cannot compare Skip with non-Skip type")

#     def __ge__(self, other):
#         if isinstance(other, Skip):
#             return True
#         raise TypeError("Cannot compare Skip with non-Skip type")


def rangeify(row: int, start: int, end: int):
    return f"{utils.num_to_column(start + 1)}{row}:{utils.num_to_column(end + 1)}{row}"


Col = int | str

Value = str | int | float


RowDict = TypeVar("RowDict", bound=dict[str, Value])


T = TypeVar("T")


class Row(ABC):
    __index = -1

    @classmethod
    def from_dict(cls: Type[T], row: dict[str, Value]) -> T:
        return cls(**row)

    @classmethod
    def from_list(cls: Type[T], row: list[Value]) -> T:
        return cls(*row)

    def to_dict(self) -> dict[str, Value]:
        return {k: v for k, v in self.__dict__.items() if k != "_Row__index"}

    def to_list(self) -> list[Value]:
        return [v for k, v in self.__dict__.items() if k != "_Row__index"]

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__annotations__:
            super().__setattr__(name, self._cast_value(name, value))
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Value:
        if name in self.__annotations__:
            return self._cast_value(name, super().__getattribute__(name))
        else:
            return super().__getattribute__(name)

    def set_index(self, index: int):
        self.__index = index

    def get_index(self) -> int:
        return self.__index

    def _is_skippable(self, name: str) -> bool:
        """Returns whether a field is skippable."""
        return self.__dataclass_fields__[name].metadata["skippable"]  # type: ignore

    def _cast_value(self, name: str, value: Value) -> Value:
        """Casts a value to the type defined in the annotations."""
        skipper = self._is_skippable(name)
        ic(name, skipper)
        if skipper and value is None:
            return None
        _type = self.__annotations__[name]
        if get_origin(_type) is Union:
            _types = get_args(_type)
            for _typ in _types:
                try:
                    return _typ(value)
                except (ValueError, TypeError):
                    pass
            raise ValueError(f"Value {value} could not be casted to any of the types in the Union: {_types}")
        else:
            return _type(value)

    @classmethod
    def col_letter(cls, name: str) -> str:
        try:
            return utils.num_to_column(list(cls.__annotations__).index(name) + 1)
        except ValueError:
            raise ValueError(f"Column {name} not found in {cls.__name__}")

    @classmethod
    def col_index(cls, col: str) -> int:
        try:
            return list(cls.__annotations__).index(col)
        except ValueError:
            raise ValueError(f"Column {col} not found in {cls.__name__}")

    def _ranges(
        self, row, force_skip: dict[str, bool] | None = None, total_override: bool = False
    ) -> list[dict[str, str | list[Value]]]:
        """Returns a list of ranges and a list of values for each range, skipping if necessary."""

        def check_skippable(key) -> bool:
            if force_skip is None:
                return self._is_skippable(key)
            elif total_override:
                return force_skip.get(key, False)
            else:
                return force_skip.get(key, self._is_skippable(key))

        values = self.to_dict()
        col_start = 0
        col_end = 0
        in_range = False
        coord_ranges = []
        val_ranges = []
        curr_range = []

        def app_range(start: int, end: int, current_values: list[Value]) -> None:
            if current_values:
                coords = f"{utils.num_to_column(col_start + 1)}{row}" if start == end else rangeify(row, start, end)
                coord_ranges.append(coords)
                val_ranges.append(current_values)

        for i, (key, val) in enumerate(values.items()):
            skippable = check_skippable(key)
            if skippable:
                if in_range:
                    app_range(col_start, col_end, curr_range)
                    curr_range = []
                    in_range = False
            else:
                if not in_range:
                    col_start = i
                    in_range = True
                col_end = i
                curr_range.append(val)
        app_range(col_start, col_end, curr_range)

        return [{"range": range, "values": [values]} for range, values in zip(coord_ranges, val_ranges)]


def rfield(default: T | None = None, skippable: bool = False) -> T:
    return field(default=default, kw_only=skippable, metadata={"skippable": skippable})  # type: ignore


RowType = TypeVar("RowType", bound=Row)


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

    def fetch_data(self):
        """Fetches all data from the sheet. Called each time __init__() is called."""
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
        """Returns a row as a dataclass instance. Row is 0-indexed."""
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


if __name__ == "__main__":

    @dataclass
    class TestRow(Row):
        Name: str = rfield()
        Age: int = rfield(skippable=True)
        Height: float = rfield()

    r = TestRow(Name="John", Height=20)
    ic(r.to_dict(), r.to_list())
    ic(r.get_index())
    ic(r._ranges(0, force_skip={"Age": True, "Height": True}))
    r.set_index(5)
