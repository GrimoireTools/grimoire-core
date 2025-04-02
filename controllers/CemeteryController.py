from typing import Self, Type

from controllers.lib.utils import gp_to_coin_list, CoinsList
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int, r_float

CEMETERY_SHEET_ID = 100792464


class CemeteryRow(Row):
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
    Death_turn: str
    Death_narrator: r_int
    Death_cause: str
    Lvl_at_death: r_int

    def to_coin_list(self) -> CoinsList:
        coin_list = [self.Money_pp, self.Money_gp, self.Money_sp, self.Money_cp]
        if None in coin_list:
            raise ValueError("Coin list incomplete")
        return CoinsList(*coin_list)  # type: ignore

    def calc_money(self) -> float:
        return self.to_coin_list().total()


class CemeteryController(SheetsControllerBase[CemeteryRow]):
    def __init__(self):
        super().__init__(CEMETERY_SHEET_ID, CemeteryRow)
