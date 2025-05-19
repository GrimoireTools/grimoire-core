from typing import Optional
from controllers.lib.base_controller import SheetsControllerBase
from controllers.pjs_controller import get_cache_name
from controllers.lib.row import Row

DT_LOG_SHEET_ID = 1238095842


class DtLogRow(Row):
    Name: str
    Discord_id: str
    Turn: int
    Info: str

    def pretty(self) -> str:
        """Returns a pretty string representation of the row."""
        return f"- Turno {self.Turn}: {self.Info}"


class DtLogController(SheetsControllerBase[DtLogRow]):
    def __init__(self):
        super().__init__(DT_LOG_SHEET_ID, DtLogRow)

    def get_user_logs(self, user_id: int) -> list[DtLogRow]:
        """Return all logs for a user, sorted descendingly by turn."""
        rows = self.get_all_rows()
        return sorted([row for row in rows if row.Discord_id == str(user_id)], key=lambda x: x.Turn, reverse=True)

    def get_user_log(self, user_id: int, turn: Optional[int] = None) -> DtLogRow | None:
        """Return the log for a user with the given turn. If turn is None, return the last log."""
        rows = self.get_user_logs(user_id)
        if len(rows) == 0:
            return None
        if turn is None:
            return rows[-1] if len(rows) > 0 else None
        for row in rows:
            if row.Turn == turn:
                return row
        return None

    def set_log(self, user_id: int, turn: int, info: str) -> DtLogRow:
        """Update the log for a user with the given turn. If the log does not exist, create a new log."""
        existing_row = self.get_user_log(user_id, turn)
        if existing_row is not None:
            existing_row.Info = info
            self.update_row(existing_row)
            return existing_row
        # If the row doesn't exist, create a new one

        row = DtLogRow(
            Name=get_cache_name(user_id),
            Discord_id=str(user_id),
            Turn=turn,
            Info=info,
        )
        self.insert_row(row)
        return row
