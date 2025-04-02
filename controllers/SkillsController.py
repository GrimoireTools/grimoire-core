from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int

SAVES_SHEET_ID = 738258837


class SkillRow(Row):
    PJ_name: str
    Discord_id: str
    Save: str
    Proficiency: str
    Bonus: r_int
    Bonus_description: str


class SkillsController(SheetsControllerBase[SkillRow]):
    def __init__(self):
        super().__init__(SAVES_SHEET_ID, SkillRow)
