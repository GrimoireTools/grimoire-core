from typing import Literal
from loguru import logger
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row

LEVEL_GROUPS_SHEET_ID = 753829510
LevelGroup = Literal["Lvl Alto", "Lvl Bajo"]
LEVEL_GROUPS: list[LevelGroup] = ["Lvl Alto", "Lvl Bajo"]


class LvlGroupRow(Row):
    Group: LevelGroup
    Level: int


LEVEL_GROUPS_CACHE: dict[str, int] = {}


def cache_lvl_groups(lvl_group_rows: list[LvlGroupRow], force: LvlGroupRow | None = None):
    """Caches the names of each character."""
    global LEVEL_GROUPS_CACHE
    LEVEL_GROUPS_CACHE = {gr.Group: gr.Level for gr in lvl_group_rows}
    if force:
        LEVEL_GROUPS_CACHE[force.Group] = force.Level
    logger.debug(f"Cached level groups: {LEVEL_GROUPS_CACHE}")


def get_cached_lvl_group(group: LevelGroup) -> int:
    """Returns the group's level."""
    global LEVEL_GROUPS_CACHE
    if group not in LEVEL_GROUPS_CACHE:
        LvlGroupController()
    return LEVEL_GROUPS_CACHE.get(group, 1)


class LvlGroupController(SheetsControllerBase[LvlGroupRow]):
    def __init__(self):
        super().__init__(LEVEL_GROUPS_SHEET_ID, LvlGroupRow)

    def _after_fetch(self):
        """
        After fetching the data, cache the level groups.
        """
        rows = self.get_all_rows()
        cache_lvl_groups(rows)

    def get_level_row(self, group: str) -> LvlGroupRow:
        """Returns the level of a given group."""
        rows = self.find_rows_with_values({"Group": group})
        if rows:
            return rows[0]
        raise ValueError(f"Group '{group}' not found in level groups.")

    def set_level(self, group: str, level: int):
        """Sets the level of a given group."""
        row = self.get_level_row(group)
        if not row:
            raise ValueError(f"Group '{group}' not found in level groups.")
        if level < 1 or level > 20:
            raise ValueError("Level must be between 1 and 20.")
        row.Level = level
        self.set_row(row)

        # Update the cache
        logger.info(f"Force caching new level value.")

        cache_lvl_groups(self.get_all_rows(), row)
        from controllers.pjs_controller import clear_pj_cache

        clear_pj_cache()

        logger.info(f"Set level {level} for group '{group}'.")
