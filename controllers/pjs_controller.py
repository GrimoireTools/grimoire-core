from typing import Self, Type

from loguru import logger

from controllers.lib.utils import gp_to_coin_list, CoinsList, DataNotFoundError
from controllers.lib.base_controller import SheetsControllerBase, Value
from controllers.lib.row import JsonData, Row

PJ_SHEET_ID = 0


class PJRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Title: str
    Classes: JsonData
    Race: str
    Subrace: str
    Alignment: str
    Downtime: float
    Money_pp: int
    Money_gp: int
    Money_ep: int
    Money_sp: int
    Money_cp: int
    Money_total: float
    Last_turn: str
    God: str
    Devotion: int
    Renombre: int
    Divine_favor: int
    Reputation: int
    Crianza: int
    Expression: int
    Mecenas: int
    Infamy: int

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
        coin_list = [self.Money_pp, self.Money_gp, self.Money_ep,
                     self.Money_sp, self.Money_cp]
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


class PJsController(SheetsControllerBase[PJRow]):
    def __init__(self):
        super().__init__(PJ_SHEET_ID, PJRow)

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
