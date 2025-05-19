from typing import Any, Self, Tuple, TypedDict
from controllers.pjs_controller import PJsController
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import JsonData, Row
from controllers.lib.utils import DataNotFoundError, not_none

MODIFIERS_SHEET_ID = 1986112206


class Contribution(TypedDict):
    name: str
    points: int


class VictoryPointsRow(Row):
    Mission_name: str
    Points: int
    Objectives: JsonData[str, int]  # {<obj_name>: points}
    Contributions: JsonData[str, Contribution]  # {user_id (str): {name: ..., points: ...}}
    Active: int

    def user_contribution(self: Self, user_id: int) -> Tuple[str, int]:
        """
        Returns the contribution of a user: the name of their PJ and the amount contributed.
        """
        str_id = str(user_id)
        if str_id in self.Contributions.keys():
            return self.Contributions[str_id]["name"], self.Contributions[str_id]["points"]
        else:
            return "Nope", 0

    def add_points(self: Self, user_id: int, amount: int):
        """
        Adds points to the row.
        Returns the previous and new point contributions of the contributing PJ.
        """
        old = 0
        new = amount
        str_id = str(user_id)
        self.Points += amount
        if str_id in self.Contributions.keys():
            old = self.Contributions[str_id]["points"]
            new = old + amount
            self.Contributions[str_id]["points"] = new
        else:
            pj = PJsController().get_pj_row(user_id)
            self.Contributions[str_id] = {"name": pj.Name, "points": new}
        return old, new

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

    def get_mission_row(self, name: str) -> VictoryPointsRow:
        """Gets the modifiers row for a given user_id."""
        try:
            return self.find_rows_with_values({"Mission_name": name})[0]
        except (ValueError, DataNotFoundError, IndexError):
            raise DataNotFoundError(
                f"Esta misión no existe. Usa /add_mission para añadirla a la lista de misiones."
            ) from None
