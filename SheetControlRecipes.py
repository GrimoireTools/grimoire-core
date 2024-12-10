import json
from functools import wraps
from typing import Any, Callable, Iterable, Self
from icecream import ic
from loguru import logger
import gspread
from gspread.utils import ValueRenderOption

from PF2eData import Recipe
import utils
from utils import Column
from varenv import getVar

RECIPES_SHEET_ID = 1160647453

credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.auth.service_account_from_dict(credentials)

recipes_sheet = gc.open("Megamarch").get_worksheet_by_id(RECIPES_SHEET_ID)


RECIPES_DATA: list[list[str]]


def update_recipe_data() -> None:
    global RECIPES_DATA
    RECIPES_DATA = recipes_sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)


def gets_recipe_data(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        update_recipe_data()
        logger.info("Updated recipe data.")
        await func(*args, **kwargs)

    return wrapped_func


class REC_COL:
    ItemName: Column = Column("A")
    ItemRarity: Column = Column("B")
    ItemType: Column = Column("C")
    ItemLevel: Column = Column("D")
    ItemRequirements: Column = Column("E")


def first_empty_recipe_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las reputaciones
    """
    column: list[str] = whole_column_rec(REC_COL.ItemName)
    return len(column) + 2


def whole_column_rec(column: utils.Column) -> list[str]:
    """
    Entrega una columna completa (sin el header)
    """
    return [row[column.excel_index()] for row in RECIPES_DATA][1:]


def update_rep_row(row_index: int, data: Iterable[Any]) -> None:
    recipes_sheet.update([data], f"A{row_index}:D{row_index}")


def row_to_Recipe(row: list[str]) -> Recipe:
    recipe: Recipe = {
        "name": row[REC_COL.ItemName.excel_index()],
        "rarity": row[REC_COL.ItemRarity.excel_index()],
        "tipo": row[REC_COL.ItemType.excel_index()],
        "level": row[REC_COL.ItemLevel.excel_index()],
        "requirements": row[REC_COL.ItemRequirements.excel_index()],
    }
    return recipe


def get_all_existing_recipes() -> list[Recipe]:
    return [row_to_Recipe(row) for row in RECIPES_DATA[1:]]


def add_recipe(name, rarity, tipo, level, requirements) -> None:
    row_index = first_empty_recipe_row()
    recipes_sheet.update([[name, rarity, tipo, level, requirements]], f"A{row_index}:E{row_index}")
