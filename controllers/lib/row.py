"""Abstract class that represents a single row in a sheet."""

from abc import ABC
from collections import OrderedDict
from dataclasses import dataclass, field
import types
from typing import Any, Dict, Generic, Type, TypeVar, Union, get_args, get_origin, get_type_hints
import json
from .utils import num_to_column, column_to_num

Col = int | str
Value = str | int | float
T = TypeVar("T")


def rangeify(row: int, start: int, end: int):
    return f"{num_to_column(start + 1)}{row}:{num_to_column(end + 1)}{row}"


def row_none_default(cls=None, **kwargs):
    def wrap(cls):
        hints = get_type_hints(cls)
        for name, type_hint in hints.items():
            if not hasattr(cls, name):
                setattr(cls, name, field(default=None))
        return dataclass(**kwargs)(cls)

    if cls is None:
        return wrap
    return wrap(cls)


class Row(ABC):
    """Abstract class that represents a single row in a sheet.

    Subclasses should define the fields as class attributes with type hints.
    Types can be str, int and float, which can be Optional.

    fields set to None are assumed to be skippable, meaning that if the value is None, it will be skipped when writing to the sheet.
    """

    __index = -1

    @classmethod
    def from_dict(cls: Type[T], row: dict[str, Value | None]) -> T:
        """Creates a new instance of the class from a dictionary."""
        return cls(**row)

    @classmethod
    def from_list(cls: Type[T], row: list[Value]) -> T:
        """Creates a new instance of the class from a list"""
        hints = get_type_hints(cls)
        keys = list(hints.keys())
        return cls(**{keys[i]: value for i, value in enumerate(row)})

    def __init__(self, **kwargs: Any) -> types.NoneType:
        """Initializes the class with none, some or all of its attributes.

        Attributes not given are set to None.
        """
        hints = get_type_hints(self)
        for name, type_hint in hints.items():
            if name not in kwargs:
                kwargs[name] = None
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.__index = -1

    def __repr__(self) -> str:
        """Returns a string representation of the row."""
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in self.__dict__.items() if k != '_Row__index')})"

    def to_dict(self) -> dict[str, Value]:
        """Returns a dictionary representation of the row."""
        hints = get_type_hints(self)
        vals = [(name, self.__getattribute__(name)) for name in hints.keys()]
        return OrderedDict(vals)

    def to_list(self) -> list[Value]:
        """Returns a list representation of the row."""
        return [v for k, v in self.__dict__.items() if k != "_Row__index"]

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets an attribute, casting it to the correct type if necessary.

        This way, when getting a value from the sheet, it is automatically casted to the correct type.
        """
        if name in self.__annotations__:
            super().__setattr__(name, self._cast_value(name, value))
        else:
            super().__setattr__(name, value)

    def set_index(self, index: int):
        """Sets the 0-based index of the row in the sheet."""
        self.__index = index

    def get_index(self) -> int:
        """Returns the 0-based index of the row in the sheet
        or -1 if the row has not been added to the sheet yet"""
        return self.__index

    def _cast_value(self, name: str, value: Value) -> Value:
        """Casts a value to the type defined in the annotations."""
        if value is None:
            return None
        _type = self.__annotations__[name]
        if get_origin(_type) in [types.UnionType, Union]:
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
            return num_to_column(list(cls.__annotations__).index(name) + 1)
        except ValueError:
            raise ValueError(f"Column {name} not found in {cls.__name__}")

    @classmethod
    def col_index(cls, col: str) -> int:
        """Return the index of a column with the given name."""
        try:
            return list(cls.__annotations__).index(col)
        except ValueError:
            raise ValueError(f"Column {col} not found in {cls.__name__}")

    def _ranges(
        self, row: int, force_set: dict[str, bool] | None = None, force_skip: dict[str, bool] | None = None
    ) -> list[dict[str, str | list[Value]]]:
        """
        Creates a list of ranges and values for each range in the row.

        For example, if the row is [1, 2, None, 4, 5, None, 7, 8, 9], the output will be:
        [
            {"range": "A1:B1", "values": [1, 2]},
            {"range": "D1:E1", "values": [4, 5]},
            {"range": "G1:I1", "values": [7, 8, 9]}
        ]

        force_set is a dictionary that can be used to force a field to be set or not set, for Optional fields.
        force_skip is a dictionary that can be used to force a field to be skipped, for non-Optional fields.

        row is 0-indexed, and converted to 1-indexed for Google Sheets.

        """
        row += 1  # Convert to 1-based index for Google Sheets
        values = self.to_dict()

        def check_skippable(key) -> bool:
            skip = values[key] is None
            if force_skip is not None:
                skip = skip or force_skip.get(key, False)
            if force_set is not None:
                skip = not force_set.get(key, skip)
            return skip

        col_start = 0
        col_end = 0
        in_range = False
        coord_ranges = []
        val_ranges = []
        curr_range = []

        def app_range(start: int, end: int, current_values: list[Value]) -> None:
            if current_values:
                coords = f"{num_to_column(col_start + 1)}{row}" if start == end else rangeify(row, start, end)
                coord_ranges.append(coords)
                val_ranges.append(current_values)

        for key, val in values.items():
            i = self.col_index(key)
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
                if isinstance(val, JsonData):
                    curr_range.append(json.dumps(val))
                else:
                    curr_range.append(val)
        app_range(col_start, col_end, curr_range)

        return [{"range": range, "values": [values]} for range, values in zip(coord_ranges, val_ranges)]


def rfield(default: T | None = None) -> T:
    """Field definition for a row dataclass."""
    return field(default=default)  # type: ignore


RowType = TypeVar("RowType", bound=Row)

r_int = Union[int, None]
r_float = Union[float, None]
r_str = Union[str, None]


K = TypeVar("K")
V = TypeVar("V")


class JsonData(Dict[K, V], Generic[K, V]):
    """A dictionary that can be serialized to JSON."""

    def __init__(self, data=None):
        """Initializes the JsonData object. If data is a list, it is converted to a dictionary with the index as the key."""
        if isinstance(data, str):
            parsed = json.loads(data)
            if isinstance(parsed, list):
                parsed = {i: v for i, v in enumerate(parsed)}
            data = dict(parsed)
        super().__init__(data or {})  # type: ignore
