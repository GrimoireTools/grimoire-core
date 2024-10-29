import json
from functools import wraps
from typing import Any, Callable
from icecream import ic

import gspread
from gspread.utils import ValueRenderOption

import utils
from utils import Column
from varenv import getVar

CEMETERY_SHEET_ID = 100792464

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.auth.service_account_from_dict(credentials)

cemetery_sheet = gc.open("Megamarch").get_worksheet_by_id(CEMETERY_SHEET_ID)


CEMETERY_DATA: list[list[str]]


def update_recipe_data() -> None:
    global CEMETERY_DATA
    CEMETERY_DATA = cemetery_sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)


def gets_cemetery_data(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        update_recipe_data()
        ic("Updated recipe data.")
        await func(*args, **kwargs)

    return wrapped_func


def first_empty_recipe_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las reputaciones
    """
    column: list[str] = whole_column_rec(Column("A"))
    return len(column) + 2


def whole_column_rec(column: utils.Column) -> list[str]:
    """
    Entrega una columna completa (sin el header)
    """
    return [row[column.excel_index()] for row in CEMETERY_DATA][1:]


def add_dead_PJ(PJ_data: list[Any], turno: int, narrador: str, causa: str, nivel: int) -> None:
    row_index = first_empty_recipe_row()
    cemetery_sheet.update([PJ_data + [turno, narrador, causa, nivel]], f"A{row_index}:S{row_index}")
