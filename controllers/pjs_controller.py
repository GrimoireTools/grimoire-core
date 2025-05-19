from typing import Literal, Self, Type

from loguru import logger

from controllers.lib.utils import gp_to_coin_list, CoinsList, DataNotFoundError
from controllers.lib.base_controller import SheetsControllerBase, Value
from controllers.lib.row import Row

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


CALIBAN_CACHE: dict[str, bool] = {}


def cache_caliban(pj_rows: list[PJRow]):
    """Caches the list of characters that have met Caliban."""
    global CALIBAN_CACHE
    CALIBAN_CACHE = {pj.Discord_id: pj.Caliban_met == 1 for pj in pj_rows}
    logger.debug(f"Cached Caliban met status: {CALIBAN_CACHE}")


def get_caliban_met(user_id: str | int) -> bool:
    """Returns True if the character has met Caliban."""
    global CALIBAN_CACHE
    user_id = str(user_id)
    if user_id not in CALIBAN_CACHE:
        PJsController()
    return CALIBAN_CACHE.get(user_id, False)


NAMES_CACHE: dict[str, str] = {}


def cache_names(pj_rows: list[PJRow]):
    """Caches the names of each character."""
    global NAMES_CACHE
    NAMES_CACHE = {pj.Discord_id: pj.Name for pj in pj_rows}
    logger.debug(f"Cached names status: {NAMES_CACHE}")


def get_cached_name(user_id: str | int) -> str:
    """Returns the user's character's name."""
    global NAMES_CACHE
    user_id = str(user_id)
    if user_id not in NAMES_CACHE:
        PJsController()
    return NAMES_CACHE.get(user_id, "Cache miss")


class PJsController(SheetsControllerBase[PJRow]):
    def __init__(self):
        super().__init__(PJ_SHEET_ID, PJRow)

    def _after_fetch(self):
        """
        After fetching the data, cache the list of characters that have met Caliban.
        """
        rows = self.get_all_rows()
        cache_caliban(rows)
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
            raise DataNotFoundError(f"Character with user_id {user_id} not found") from None

    def character_exists(self, user_id: int) -> bool:
        try:
            return self.get_pj_row(user_id) is not None
        except DataNotFoundError:
            return False
