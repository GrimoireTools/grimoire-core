from loguru import logger

from controllers.lib.utils import DataNotFoundError
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import JsonData, Row
from system_data import PREDEFINED_ABILITIES, Attribute, Ability, Resource, KNOWLEDGES, TALENTS, SKILLS

PJ_SHEET_ID = 0  # TODO: set real sheet ID


class PJRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Last_turn: int
    Char_type: str
    SubChar_type: JsonData[str, str]
    Attributes: JsonData[Attribute, int]
    Abilities: JsonData[Ability, int]
    Specialties: JsonData[Ability | Attribute, str]
    Resources: JsonData[Resource, int]

    def subtype(self, subtype: str, set_value: str | None = None) -> str | int:
        """Returns the current value of a subtype, optionally setting a new value."""
        if set_value is not None:
            self.SubChar_type[subtype] = set_value
        return self.SubChar_type.get(subtype, "")

    def resource(self, resource: Resource, set_value: int | None = None) -> int:
        """Returns the current value of a resource, optionally setting a new value."""
        if set_value is not None:
            self.Resources[resource] = set_value
        return self.Resources.get(resource, 0)

    def ability(self, ability: Ability, set_value: int | None = None) -> int:
        """Returns the current value of an ability, optionally setting a new value."""
        if set_value is not None:
            self.Abilities[ability] = set_value
        return self.Abilities.get(ability, 0)

    def attribute(self, attribute: Attribute, set_value: int | None = None) -> int:
        """Returns the current value of an attribute, optionally setting a new value."""
        if set_value is not None:
            self.Attributes[attribute] = set_value
        return self.Attributes.get(attribute, 0)

    def specialty(self, ability: Ability | Attribute, set_value: str | None = None) -> str:
        """Returns the current specialty of an ability or attribute, optionally setting a new one."""
        if set_value is not None:
            self.Specialties[ability] = set_value
        return self.Specialties.get(ability, "")

    def set_subtype(self, subtypes: dict[str, str]) -> None:
        self.SubChar_type.update(subtypes)

    def set_attributes(self, attributes: dict[Attribute, int]) -> None:
        self.Attributes.update(attributes)

    def set_abilities(self, abilities: dict[Ability, int]) -> None:
        self.Abilities.update(abilities)

    def set_specialties(self, specialties: dict[Ability | Attribute, str]) -> None:
        self.Specialties.update(specialties)

    def set_resources(self, resources: dict[Resource, int]) -> None:
        self.Resources.update(resources)

    def max_attr(self) -> int:
        """Return the max value an attribute can have based on the character type."""
        if self.Char_type == "Vampire":
            match self.SubChar_type["Generation"]:
                case "5":
                    return 8
                case "6":
                    return 7
                case "7":
                    return 6
                case _:
                    return 5
        else:
            return 5  # Default max for other character types

    def full_abilities(self) -> dict[Ability, int]:
        """Return a dictionary of all abilities, including predefined and custom ones."""
        all_abilities = {ability: self.Abilities.get(ability, 0) for ability in PREDEFINED_ABILITIES}
        all_abilities.update(
            {ability: value for ability, value in self.Abilities.items() if ability not in PREDEFINED_ABILITIES}
        )
        return all_abilities

    def knowledge_abilities(self, all: bool = False) -> dict[Ability, int]:
        """Return a dictionary of all knowledge abilities."""
        if all:
            return {ability: self.Abilities.get(ability, 0) for ability in KNOWLEDGES}
        else:
            return {ability: value for ability, value in self.Abilities.items() if ability in KNOWLEDGES and value > 0}

    def talent_abilities(self, all: bool = False) -> dict[Ability, int]:
        """Return a dictionary of all talent abilities."""
        if all:
            return {ability: self.Abilities.get(ability, 0) for ability in TALENTS}
        else:
            return {ability: value for ability, value in self.Abilities.items() if ability in TALENTS and value > 0}

    def skill_abilities(self, all: bool = False) -> dict[Ability, int]:
        """Return a dictionary of all skill abilities."""
        if all:
            return {ability: self.Abilities.get(ability, 0) for ability in SKILLS}
        else:
            return {ability: value for ability, value in self.Abilities.items() if ability in SKILLS and value > 0}

    def custom_abilities(self) -> dict[Ability, int]:
        """Return a dictionary of all custom abilities (not predefined)."""
        return {ability: value for ability, value in self.Abilities.items() if ability not in PREDEFINED_ABILITIES}


class PJsController(SheetsControllerBase[PJRow]):
    def __init__(self) -> None:
        super().__init__(PJ_SHEET_ID, PJRow)

    def get_pj_row(self, user_id: int) -> PJRow:
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except ValueError as e:
            logger.exception(f"Character with user_id {user_id} not found: {e}")
            raise DataNotFoundError(f"Character with user_id {user_id} not found: {e.__traceback__}") from None

    def character_exists(self, user_id: int) -> bool:
        try:
            return self.get_pj_row(user_id) is not None
        except DataNotFoundError:
            return False
