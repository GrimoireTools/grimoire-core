from dataclasses import dataclass
from typing import Self, Type
from base import SKIP, SheetsControllerBase, Row, rfield, Val, Skip
from utils import CharacterNotFoundError, gp_to_coin_list

PJ_SHEET_ID = 0


@dataclass
class PJRow(Row):
    Name: Val[str] = rfield()
    Discord_id: Val[str] = rfield()
    Player: Val[str] = rfield()
    Class: Val[str] = rfield()
    Arquetypes: Val[str] = rfield()
    Ancestry: Val[str] = rfield()
    Heritage: Val[str] = rfield()
    Downtime: Val[int] = rfield()
    Money_pp: Val[int] = rfield()
    Money_gp: Val[int] = rfield()
    Money_sp: Val[int] = rfield()
    Money_cp: Val[int] = rfield()
    Money_total: Val[float] = rfield()
    Languages: Val[str] = rfield()
    Religion: Val[str] = rfield()
    Last_turn: Val[str] = rfield()

    @classmethod
    def from_coin_list(cls: Type[Self], coin_list: list[int]) -> Self:
        instance = cls()
        instance.Money_pp = coin_list[0]
        instance.Money_gp = coin_list[1]
        instance.Money_sp = coin_list[2]
        instance.Money_cp = coin_list[3]
        return instance

    def to_coin_list(self) -> list[int]:
        coin_list = [self.Money_pp, self.Money_gp, self.Money_sp, self.Money_cp]
        for c in coin_list:
            if c == SKIP:
                raise ValueError("Coin list incomplete")
        return coin_list  # type: ignore

    def calc_money(self) -> float:
        return self.Money_pp * 10 + self.Money_gp + self.Money_sp * 0.1 + self.Money_cp * 0.01


class PJSheetController(SheetsControllerBase[PJRow]):
    def __init__(self):
        super().__init__(PJ_SHEET_ID, PJRow)

    def set_money(self, user_id: int, total_money: float):
        row = self.find_pj_row_index(user_id)
        coin_list = gp_to_coin_list(total_money)
        self.set_row(PJRow.from_coin_list(coin_list), row)

    def get_pj_row(self, user_id: int) -> PJRow:
        return self.get_row(self.find_pj_row_index(user_id))


if __name__ == "__main__":
    coin_list = gp_to_coin_list(123.45)
    print(coin_list)
    print(PJRow.from_coin_list(coin_list))
