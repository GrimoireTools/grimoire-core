from typing import Any, Self, Tuple
from PF2eData import ABILITIES, Ability
from controllers.pjs_controller import PJsController
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import JsonData, Row
from controllers.lib.utils import DataNotFoundError, not_none

MODIFIERS_SHEET_ID = 41455486


class VictoryPointsRow(Row):
    Mission_name: str
    Points: int
    Objectives: JsonData
    Contributions: JsonData
    Active: int

    def change_contribution(
        self,
        user_id: int,
        contribution: int,
    ) -> None:
        """
        Adds a contribution to the row.
        """

        # Ensure that the contributions field is a dictionary
        if not isinstance(self.Contributions, JsonData):
            self.Contributions = JsonData({})

        if user_id in self.Contributions:
            # If the user_id already exists, update the contribution
            self.Contributions[user_id]["points"] += contribution
        else:
            # If the user_id does not exist, create a new entry
            pj = PJsController().get_pj_row(user_id)
            self.Contributions[user_id] = {"points": contribution, "pj": pj.Name}

    def change_objective(self, obj_name: str, obj_pts: int):
        """
        Adds a mission to the row.
        """
        # Ensure that the objectives field is a dictionary
        if not isinstance(self.Objectives, JsonData):
            self.Objectives = JsonData({})

        if obj_name in self.Objectives:
            # If the mission_name already exists, update the points
            self.Objectives[obj_name] += obj_pts
        else:
            # If the mission_name does not exist, create a new entry
            self.Objectives[obj_name] = obj_pts

    def remove_objective(self, obj_name: str):
        """
        Removes a mission from the row.
        """
        # Ensure that the objectives field is a dictionary
        if not isinstance(self.Objectives, JsonData):
            self.Objectives = JsonData({})

        if obj_name in self.Objectives:
            # If the mission_name already exists, remove it
            del self.Objectives[obj_name]


class VictoryPointsController(SheetsControllerBase[VictoryPointsRow]):
    def __init__(self):
        super().__init__(MODIFIERS_SHEET_ID, VictoryPointsRow)

    def get_mods_row(self, user_id: int) -> VictoryPointsRow:
        """Gets the modifiers row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError(
                f"Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            ) from None
