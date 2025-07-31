"""Roles Controller Module."""

from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import JsonData, Row
from controllers.lib.utils import DataNotFoundError

ROLES_SHEET_ID = 41455486

ROLES = {
    "Healer": "🩹",
    "Tanque": "🛡️",
    "DPS": "⚔️",
    "Support": "🪄",
    "Utility": "🔧",
}


class RolesRow(Row):
    """Row for a roles entry."""

    PJ_name: str
    Discord_id: str
    Role: JsonData[int, str]  # {index: role}


class RolesController(SheetsControllerBase[RolesRow]):
    """Controller for managing roles."""

    def __init__(self) -> None:
        super().__init__(ROLES_SHEET_ID, RolesRow)

    def get_roles_row(self, user_id: int) -> RolesRow:
        """Get the roles row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError("Tu personaje no tiene roles definidos. Definelos con /set_roles.") from None

    def roles_row_exists(self, user_id: int) -> bool:
        """Check if the roles row exists for a given user_id."""
        try:
            r = self.get_roles_row(user_id)
            return r is not None and True
        except DataNotFoundError:
            return False
