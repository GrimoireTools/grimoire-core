"""GM Controller Module."""

from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row

GM_SHEET_ID = 132009121


class GMRow(Row):
    """Row for a GM entry."""

    Name: str
    Discord_id: str
    Tag: str
    Notion_mission_tag: str


class GMController(SheetsControllerBase[GMRow]):
    """Controller for managing GM entries."""

    def __init__(self) -> None:
        super().__init__(GM_SHEET_ID, GMRow)
