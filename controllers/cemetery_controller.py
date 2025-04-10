from typing import Self, Type

from controllers.lib.utils import CoinsList
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row, r_int, r_float
from controllers.pjs_controller import PJRow

CEMETERY_SHEET_ID = 100792464


class CemeteryRow(Row):
    Name: str
    Discord_id: str
    Player: str
    Class: str
    Archetypes: str
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
    Death_narrator: str
    Death_cause: str
    Lvl_at_death: r_int

    def to_coin_list(self) -> CoinsList:
        coin_list = [self.Money_pp, self.Money_gp, self.Money_sp, self.Money_cp]
        if None in coin_list:
            raise ValueError("Coin list incomplete")
        return CoinsList(*coin_list)  # type: ignore

    def calc_money(self) -> float:
        return self.to_coin_list().total()

    @classmethod
    def from_pj_row(
        cls: Type[Self],
        pj_row: PJRow,
        death_turn: str,
        death_narrator: str,
        death_cause: str,
        lvl_at_death: int,
    ) -> Self:
        """
        Convierte una fila de PJ a una fila de cementerio
        """
        return cls.from_dict(
            {
                "Name": pj_row.Name,
                "Discord_id": pj_row.Discord_id,
                "Player": pj_row.Player,
                "Class": pj_row.Class,
                "Archetypes": pj_row.Archetypes,
                "Ancestry": pj_row.Ancestry,
                "Heritage": pj_row.Heritage,
                "Downtime": pj_row.Downtime,
                "Money_pp": pj_row.Money_pp,
                "Money_gp": pj_row.Money_gp,
                "Money_sp": pj_row.Money_sp,
                "Money_cp": pj_row.Money_cp,
                "Money_total": pj_row.Money_total,
                "Languages": pj_row.Languages,
                "Religion": pj_row.Religion,
                "Death_turn": death_turn,
                "Death_narrator": death_narrator,
                "Death_cause": death_cause,
                "Lvl_at_death": lvl_at_death,
            }
        )


class CemeteryController(SheetsControllerBase[CemeteryRow]):
    def __init__(self):
        super().__init__(CEMETERY_SHEET_ID, CemeteryRow)
