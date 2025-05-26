from typing import Any, Literal, Self, Type, TypeVar, TypedDict

from loguru import logger

from controllers.lib.utils import gp_to_coin_list, CoinsList, DataNotFoundError
from controllers.lib.base_controller import SheetsControllerBase, Value
from controllers.lib.row import Row
from controllers.lvl_groups_controller import LEVEL_GROUPS, LevelGroup, get_cached_lvl_group

PJ_SHEET_ID = 0


class PJRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Class: str
    Archetypes: str
    Ancestry: str
    Heritage: str
    Downtime: int
    Money_pp: int
    Money_gp: int
    Money_sp: int
    Money_cp: int
    Money_total: float
    Languages: str
    Religion: str
    Last_turn: str
    Caliban_met: int
    Level_group: LevelGroup

    @classmethod
    def from_coin_list(cls: Type[Self], coin_list: list[int] | CoinsList) -> Self:
        """
        Convierte una lista de monedas a una fila
        """
        return cls.from_dict(
            {
                "Money_pp": coin_list[0],
                "Money_gp": coin_list[1],
                "Money_sp": coin_list[2],
                "Money_cp": coin_list[3],
            }
        )

    def level(self) -> int:
        """
        Devuelve el nivel del personaje
        """
        return get_cached_lvl_group(self.Level_group)

    def to_coin_list(self) -> CoinsList:
        """
        Convierte la fila a una lista de monedas
        """
        coin_list = [self.Money_pp, self.Money_gp, self.Money_sp, self.Money_cp]
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
        self.Money_sp = coins[2]
        self.Money_cp = coins[3]

    def add_language(self, language: str) -> None:
        """
        Añade un idioma a la fila
        """
        if self.Languages in ["", None]:
            self.Languages = language
        else:
            self.Languages += f", {language}"

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


class PjCache(TypedDict):
    Level: int
    Caliban: bool
    Name: str
    Level_group: LevelGroup


PJ_CACHE: dict[str, PjCache] = {}


def cache_pjs(pj_rows: list[PJRow]):
    """Caches the list of characters that have met Caliban."""
    global PJ_CACHE
    PJ_CACHE = {
        pj.Discord_id: {
            "Level": pj.level(),
            "Caliban": pj.Caliban_met == 1,
            "Name": pj.Name,
            "Level_group": pj.Level_group,
        }
        for pj in pj_rows
    }
    logger.debug(f"Cached PJ data: {PJ_CACHE}")


K = TypeVar("K")


def _get_cache(user_id: str | int, key: str, default: K) -> K:
    """Helper function to get a value from the cache."""
    global PJ_CACHE
    user_id = str(user_id)
    if user_id not in PJ_CACHE:
        PJsController()
    if user_id not in PJ_CACHE:
        logger.warning(f"User ID {user_id} not found in PJ_CACHE.")
        return default
    return PJ_CACHE[user_id].get(key, default)


def get_caliban_met(user_id: str | int) -> bool:
    """Returns True if the character has met Caliban."""
    return _get_cache(user_id, "Caliban", False)


def get_cached_level(user_id: str | int) -> int:
    """Returns the user's character's level."""
    return _get_cache(user_id, "Level", 1)


def get_cached_name(user_id: str | int) -> str:
    """Returns the user's character's name."""
    return _get_cache(user_id, "Name", "Desconocido")


def get_cached_group(user_id: str | int) -> LevelGroup:
    """Returns the user's character's group."""
    return _get_cache(user_id, "Level_group", LEVEL_GROUPS[0])


class PJsController(SheetsControllerBase[PJRow]):
    def __init__(self):
        super().__init__(PJ_SHEET_ID, PJRow)

    def _after_fetch(self):
        """
        After fetching the data, cache the list of characters that have met Caliban.
        """
        rows = self.get_all_rows()
        cache_pjs(rows)

    def set_money(self, user_id: int, total_money: float):
        row = self.find_pj_row_index(user_id)
        coin_list = gp_to_coin_list(total_money)
        self.set_row(PJRow.from_coin_list(coin_list), row)
        return coin_list

    def get_pj_row(self, user_id: int) -> PJRow:
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except ValueError as e:
            raise DataNotFoundError(f"Character with user_id {user_id} not found") from None

    def character_exists(self, user_id: int) -> bool:
        try:
            return self.get_pj_row(user_id) is not None
        except DataNotFoundError:
            return False
