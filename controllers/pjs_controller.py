from typing import Literal, Self, Type, TypedDict

from controllers.lib.utils import gp_to_coin_list, CoinsList, DataNotFoundError
from controllers.lib.base_controller import SheetsControllerBase, Value
from controllers.lib.row import JsonData, Row
from system_data import Class

PJ_SHEET_ID = 1585623869

Resource = Literal["Devoción", "Renombre", "Favor Divino",
                   "Reputación", "Crianza", "Expresión", "Mecenas", "Infamia"]
RESOURCES: list[Resource] = [
    "Devoción",
    "Renombre",
    "Favor Divino",
    "Reputación",
    "Crianza",
    "Expresión",
    "Mecenas",
    "Infamia",
]
res_to_attr: dict[Resource, str] = {
    "Devoción": "Devotion",
    "Renombre": "Renown",
    "Favor Divino": "Divine_favor",
    "Reputación": "Reputation",
    "Crianza": "Crianza",
    "Expresión": "Expression",
    "Mecenas": "Mecenas",
    "Infamia": "Infamy",
}


class PJRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Char_type: str
    Attributes: JsonData
    Skills: JsonData
    Resources: JsonData

    @classmethod
    def partial_create(
        cls: Type[Self],
        name: str,
        discord_id: int,
        player: str,
        title: str,
        clase: str,
        race: str,
        alignment: str,
        god: str,
    ) -> dict:
        """
        Crea un personaje parcial, al que le falta solamente la subraza y completar los nieveles de las clases.
        """
        return {
            "Name": name,
            "Discord_id": discord_id,
            "Player": player,
            "Title": title,
            "Classes": {clase: ["", 1]},
            "Race": race,
            "Alignment": alignment,
            "Downtime": 0,
            "Money_pp": 0,
            "Money_gp": 0,
            "Money_ep": 0,
            "Money_sp": 0,
            "Money_cp": 0,
            "Money_total": None,
            "Last_turn": "-",
            "God": god,
            "Devotion": 0,
            "Renown": 0,
            "Divine_favor": 0,
            "Reputation": 0,
            "Crianza": 0,
            "Expression": 0,
            "Mecenas": 0,
            "Infamy": 0,
        }

    @classmethod
    def from_coin_list(cls: Type[Self], coin_list: list[int] | CoinsList) -> Self:
        """
        Convierte una lista de monedas a una fila
        """
        return cls.from_dict(
            {
                "Money_pp": coin_list[0],
                "Money_gp": coin_list[1],
                "Money_ep": coin_list[2],
                "Money_sp": coin_list[3],
                "Money_cp": coin_list[4],
            }
        )

    def to_coin_list(self) -> CoinsList:
        """
        Convierte la fila a una lista de monedas
        """
        coin_list = [self.Money_pp, self.Money_gp,
                     self.Money_ep, self.Money_sp, self.Money_cp]
        if None in coin_list:
            raise ValueError("Coin list incomplete")
        return CoinsList(*coin_list)  # type: ignore

    def calc_money(self) -> float:
        """
        Calcula el dinero total en gp
        """
        return self.to_coin_list().total()

    def update_money(self, coins: float | list[int] | CoinsList) -> None:
        """
        Actualiza el dinero en la fila
        """
        if isinstance(coins, (float, int)):
            coins = gp_to_coin_list(coins)
        self.Money_pp = coins[0]
        self.Money_gp = coins[1]
        self.Money_ep = coins[2]
        self.Money_sp = coins[3]
        self.Money_cp = coins[4]

    def _ranges(
        self, row: int, force_set: dict[str, bool] | None = None, force_skip: dict[str, bool] | None = None
    ) -> list[dict[str, str | list[Value]]]:
        """
        Convierte la fila a un rango de Google Sheets
        """
        if force_skip is None:
            force_skip = {}
        force_skip["Money_total"] = True
        return super()._ranges(row, force_set, force_skip)

    def pretty_classes(self) -> str:
        """
        Devuelve una cadena con las clases del personaje
        """
        classes = self.Classes
        if not classes:
            return "Sin clases"
        classes = [f"{subclass} {cls} {level}".strip()
                   for cls, (subclass, level) in classes.items()]
        return ", ".join(classes)

    def resource(self, resource: Resource, set_add: int | None = None, relative: bool = True) -> int:
        """
        Devuelve el recurso del personaje, seteandolo antes si se le pasa `set`
        """
        if resource not in RESOURCES:
            raise ValueError(f"{resource} no es un recurso válido")
        attr = res_to_attr[resource]
        if set_add is not None:
            if relative:
                current = getattr(self, attr, 0)
                setattr(self, attr, current + set_add)
            else:
                setattr(self, attr, set_add)
        return getattr(self, attr, 0)


NAMES_CACHE: dict[str, str] = {}


def cache_names(pj_rows: list[PJRow]):
    """Caches the name of the character of each player."""
    global NAMES_CACHE
    NAMES_CACHE = {pj.Discord_id: pj.Name for pj in pj_rows}


def get_cache_name(user_id: str | int) -> str:
    """Returns the cached name associated with a user_id."""
    global NAMES_CACHE
    if not NAMES_CACHE:
        PJsController()
    return NAMES_CACHE.get(str(user_id), "Desconocido")


class PJsController(SheetsControllerBase[PJRow]):
    def __init__(self):
        super().__init__(PJ_SHEET_ID, PJRow)

    def _after_fetch(self):
        """
        After fetching the data, cache the list of each character.
        """
        rows = self.get_all_rows()
        cache_names(rows)

    def set_money(self, user_id: int, total_money: float):
        row = self.find_pj_row_index(user_id)
        coin_list = gp_to_coin_list(total_money)
        self.set_row(PJRow.from_coin_list(coin_list), row)
        return coin_list

    def get_pj_row(self, user_id: int) -> PJRow:
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except ValueError as e:
            raise DataNotFoundError(
                f"Character with user_id {user_id} not found") from None

    def character_exists(self, user_id: int) -> bool:
        try:
            return self.get_pj_row(user_id) is not None
        except DataNotFoundError:
            return False
