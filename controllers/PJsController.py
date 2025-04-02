from typing import Self, Type

from controllers.lib.utils import gp_to_coin_list, CoinsList
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int, r_float

PJ_SHEET_ID = 0


class PJRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Class: str
    Arquetypes: str
    Ancestry: str
    Heritage: str
    Downtime: r_int
    Money_pp: r_int
    Money_gp: r_int
    Money_sp: r_int
    Money_cp: r_int
    Money_total: r_float
    Languages: str
    Religion: str
    Last_turn: str
    Caliban_met: r_int

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

    def update_money(self, coins: int | list[int] | CoinsList) -> None:
        """
        Actualiza el dinero en la fila
        """
        if isinstance(coins, int):
            coins = gp_to_coin_list(coins)
        self.Money_pp = coins[0]
        self.Money_gp = coins[1]
        self.Money_sp = coins[2]
        self.Money_cp = coins[3]


class PJsController(SheetsControllerBase[PJRow]):
    def __init__(self):
        super().__init__(PJ_SHEET_ID, PJRow)

    def set_money(self, user_id: int, total_money: float):
        row = self.find_pj_row_index(user_id)
        coin_list = gp_to_coin_list(total_money)
        self.set_row(PJRow.from_coin_list(coin_list), row)
        return coin_list

    def get_pj_row(self, user_id: int) -> PJRow:
        return self.get_row(self.find_pj_row_index(user_id))
