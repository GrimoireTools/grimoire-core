from controllers.lib.utils import DataNotFoundError
from controllers.lib.base_controller import SheetsControllerBase
from controllers.pjs_controller import Attribute, Ability, Resource
from controllers.lib.row import JsonData, Row

CEMETERY_SHEET_ID = 416758615


class CemeteryRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Turn_of_death: int
    Cause_of_death: str
    Char_type: str
    Attributes: JsonData[Attribute, int]
    Abilities: JsonData[Ability, int]
    Specialties: JsonData[Ability, str]
    Resources: JsonData[Resource, int]

    def resource(self, resource: Resource, set_value: int | None = None) -> int:
        if set_value is not None:
            self.Resources[resource] = set_value
        return self.Resources.get(resource, 0)

    def ability(self, ability: Ability, set_value: int | None = None) -> int:
        if set_value is not None:
            self.Abilities[ability] = set_value
        return self.Abilities.get(ability, 0)

    def attribute(self, attribute: Attribute, set_value: int | None = None) -> int:
        if set_value is not None:
            self.Attributes[attribute] = set_value
        return self.Attributes.get(attribute, 0)

    def specialty(self, ability: Ability, set_value: str | None = None) -> str:
        if set_value is not None:
            self.Specialties[ability] = set_value
        return self.Specialties.get(ability, "")

    def set_attributes(self, attributes: dict[Attribute, int]):
        self.Attributes.update(attributes)

    def set_abilities(self, abilities: dict[Ability, int]):
        self.Abilities.update(abilities)

    def set_resources(self, resources: dict[Resource, int]):
        self.Resources.update(resources)


class CemeteryController(SheetsControllerBase[CemeteryRow]):
    def __init__(self):
        super().__init__(CEMETERY_SHEET_ID, CemeteryRow)

    def get_row_by_user(self, user_id: int) -> CemeteryRow:
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except ValueError:
            raise DataNotFoundError(
                f"No deceased character found for user_id {user_id}"
            ) from None

    def character_exists(self, user_id: int) -> bool:
        try:
            return self.get_row_by_user(user_id) is not None
        except DataNotFoundError:
            return False
