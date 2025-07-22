"""Controller module for managing proficiency rows in a sheet.

Provides a base controller class for handling proficiency-related operations
such as retrieving, searching, and validating proficiency rows for users.

Example:
```python
controller = ProficiencyControllerBase(sheet_id=123, cls=RowType, prof_row_name="Skill")
row = controller.get_prof_row(user_id=456, prof_name="Stealth")
```

Important Classes:
    - ProficiencyControllerBase: Base class for proficiency row operations.
"""

from .base_controller import SheetsControllerBase
from .row import RowType
from .utils import DataNotFoundError


class ProficiencyControllerBase(SheetsControllerBase[RowType]):
    """Base class for proficiency controllers."""

    _prof_row_name: str

    def __init__(self, sheet_id: int, cls: type[RowType], prof_row_name: str) -> None:
        super().__init__(sheet_id, cls)
        self._prof_row_name = prof_row_name

    def get_prof_row(self, user_id: int, prof_name: str) -> RowType | None:
        """Get a proficiency row by user_id and proficiency name."""
        try:
            return self.find_rows_with_values({"Discord_id": str(user_id), self._prof_row_name: prof_name})[0]
        except (ValueError, IndexError):
            return None

    def get_prof_row_strict(self, user_id: int, prof_name: str) -> RowType:
        """Get a proficiency row by user_id and proficiency name. Raises CharacterNotFoundError if not found."""
        row = self.get_prof_row(user_id, prof_name)
        if row is None:
            raise DataNotFoundError(f"Proficiency '{prof_name}' for character with user_id {user_id} not found")
        return row

    def get_all_prof_rows(self, user_id: int) -> list[RowType]:
        """Get all proficiency rows for a given user_id."""
        try:
            rows = self.find_rows_with_values({"Discord_id": str(user_id)})
            if not rows:
                raise DataNotFoundError(f"Proficiencies for character with user_id {user_id} not found (empty rows)")
            return rows
        except ValueError:
            raise DataNotFoundError(f"Proficiencies for characters with user_id {user_id} not found") from None
