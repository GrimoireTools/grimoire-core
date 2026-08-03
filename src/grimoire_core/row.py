"""Abstract class that represents a single row in a sheet."""

import json
import types
from collections import OrderedDict
from dataclasses import field
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, Union, get_args, get_origin, get_type_hints

from grimoire_core.utils import num_to_column

if TYPE_CHECKING:
    from collections.abc import Mapping

Col = int | str
Value = str | int | float
T = TypeVar("T")


def rangeify(row: int, start: int, end: int) -> str:
    """Return a range string for a given row and start/end columns.

    The row is 1-indexed, and the start and end columns are 0-indexed.
    For example, if row=1, start=0, end=2, the output will be "A1:C1".
    """
    return f"{num_to_column(start + 1)}{row}:{num_to_column(end + 1)}{row}"


class Row:
    """Abstract class that represents a single row in a sheet.

    Subclasses should define the fields as class attributes with type hints.
    Types can be str, int and float, which can be Optional.

    fields set to None are assumed to be skippable, meaning that if the value is None,
    it will be skipped when writing to the sheet.
    """

    __index = -1

    @classmethod
    def from_dict(cls: type[T], row: dict[str, Value | None]) -> T:
        """Create a new instance of the class from a dictionary."""
        return cls(**row)

    @classmethod
    def from_list(cls: type[T], row: list[Value]) -> T:
        """Create a new instance of the class from a list."""
        hints = get_type_hints(cls)
        keys = list(hints.keys())
        return cls(**{keys[i]: value for i, value in enumerate(row)})

    def __init__(self, **kwargs: Any) -> types.NoneType:
        """Initialize the class with none, some or all of its attributes.

        Attributes not given are set to None.
        """
        hints = get_type_hints(type(self))
        for name, _type_hint in hints.items():
            if name not in kwargs:
                kwargs[name] = None
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.__index = -1

    def __repr__(self) -> str:
        """Return a string representation of the row."""
        return (
            f"{self.__class__.__name__}"
            f"({', '.join(f'{k}={v}' for k, v in self.__dict__.items() if k != '_Row__index')})"
        )

    def to_dict(self) -> dict[str, Value]:
        """Return a dictionary representation of the row."""
        hints = get_type_hints(type(self))
        vals = [(name, self.__getattribute__(name)) for name in hints]
        return OrderedDict(vals)

    def to_list(self) -> list[Value]:
        """Return a list representation of the row."""
        return [v for k, v in self.__dict__.items() if k != "_Row__index"]

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute, casting it to the correct type if necessary.

        This way, when getting a value from the sheet, it is automatically casted to the correct type.
        """
        if name in get_type_hints(type(self)):
            super().__setattr__(name, self._cast_value(name, value))
        else:
            super().__setattr__(name, value)

    def set_index(self, index: int) -> None:
        """Set the 0-based index of the row in the sheet."""
        self.__index = index

    def get_index(self) -> int:
        """Return the 0-based index of the row in the sheet or -1 if the row has not been added to the sheet yet."""
        return self.__index

    def _cast_value(self, name: str, value: Value) -> Value:
        """Cast a value to the type defined in the annotations."""
        if value is None:
            return None
        _type = get_type_hints(type(self))[name]
        if get_origin(_type) in [types.UnionType, Union]:
            _types = get_args(_type)
            for _typ in _types:
                try:
                    return _typ(value)
                except ValueError, TypeError:
                    pass
            raise ValueError(f"Value {value} could not be casted to any of the types in the Union: {_types}")
        elif get_origin(_type) is Literal:
            lit_vals = get_args(_type)
            for lit_val in lit_vals:
                try:
                    val = type(lit_val)(value)
                    if val == lit_val:
                        return val
                except ValueError, TypeError:
                    continue
            raise ValueError(f"Value {value} is not in the Literal: {lit_vals}")
        else:
            return _type(value)

    @classmethod
    def col_letter(cls, name: str) -> str:
        """Return the letter of a column with the given name."""
        try:
            return num_to_column(list(cls.__annotations__).index(name) + 1)
        except ValueError as e:
            raise ValueError(f"Column {name} not found in {cls.__name__}") from e

    @classmethod
    def col_index(cls, col: str) -> int:
        """Return the index of a column with the given name."""
        try:
            return list(cls.__annotations__).index(col)
        except ValueError as e:
            raise ValueError(f"Column {col} not found in {cls.__name__}") from e

    def _ranges(
        self, row: int, force_set: dict[str, bool] | None = None, force_skip: dict[str, bool] | None = None
    ) -> list[dict[str, str | list[Value]]]:
        """
        Create a list of ranges and values for each range in the row.

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

        def check_skippable(key: str) -> bool:
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

        return [{"range": range, "values": [values]} for range, values in zip(coord_ranges, val_ranges, strict=False)]


def rfield(default: T | None = None) -> T:
    """Field definition for a row dataclass."""
    return field(default=default)  # type: ignore


RowType = TypeVar("RowType", bound=Row)

r_int = int | None
r_float = float | None
r_str = str | None


K = TypeVar("K")
V = TypeVar("V")


class JsonData(dict[K, V], Generic[K, V]):
    """A dictionary that can be serialized to JSON."""

    def __init__(self, data: Mapping[Any, Any] | str | None = None) -> None:
        """Initializes the JsonData object.

        If data is a list, it is converted to a dictionary with the index as the key.
        """
        if isinstance(data, str):
            parsed = json.loads(data)
            if isinstance(parsed, list):
                parsed = dict(enumerate(parsed))
            data = dict(parsed)
        super().__init__(data or {})  # type: ignore
