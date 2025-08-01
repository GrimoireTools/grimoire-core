"""GM Controller Module."""

from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row
from controllers.lib.utils import DataNotFoundError

GM_SHEET_ID = 132009121


class GMRow(Row):
    """Row for a GM entry."""

    Name: str
    Discord_id: str
    Tag_name: str
    Notion_mission_tag: str
    Emoji: str


class GMController(SheetsControllerBase[GMRow]):
    """Controller for managing GM entries."""

    def __init__(self) -> None:
        super().__init__(GM_SHEET_ID, GMRow)

    def get_gm_row(self, user_id: int) -> GMRow:
        """Get the GM row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError("No tienes tus datos de GM definidos. Definelos con `/register_gm`.") from None

    def gm_row_exists(self, user_id: int) -> bool:
        """Check if the GM row exists for a given user_id."""
        try:
            r = self.get_gm_row(user_id)
            return r is not None and True
        except DataNotFoundError:
            return False
