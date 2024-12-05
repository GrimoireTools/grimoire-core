import json
from functools import wraps
from typing import Any, Callable, Tuple, TypedDict
from icecream import ic

import gspread
from gspread.utils import ValueRenderOption

import utils
from PF2eData import ABILITIES, SKILLS, PROF_BONUSES, Ability
from utils import Column
from varenv import getVar
from SheetControl import get_level_global

SAVES_SHEET_ID = 1756443107
ABILITIES_SHEET_ID = 41455486


credentials = json.loads(getVar("GOOGLE"), strict=False)

gc = gspread.auth.service_account_from_dict(credentials)

save_sheet = gc.open("Megamarch").get_worksheet_by_id(SAVES_SHEET_ID)
ability_sheet = gc.open("Megamarch").get_worksheet_by_id(ABILITIES_SHEET_ID)

SAVE_DATA: list[list[str]]
ABILITY_DATA: list[list[str]]


def _update_save_data() -> None:
    "Actualiza los singletons SKILL_DATA, ABILITY_DATA"
    global SAVE_DATA, ABILITY_DATA
    SAVE_DATA = save_sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)
    ABILITY_DATA = ability_sheet.get_all_values(value_render_option=ValueRenderOption.unformatted)


def gets_save_data(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        _update_save_data()
        ic("Updated save/ability data.")
        await func(*args, **kwargs)

    return wrapped_func


class SAVE_COL:
    Name: Column = Column("A")
    Discord_id: Column = Column("B")
    Save: Column = Column("C")
    Proficiency: Column = Column("D")
    ExtraBonuses: Column = Column("E")
    ExtraDescription: Column = Column("F")


class ABILITY_COL:
    Name: Column = Column("A")
    Discord_id: Column = Column("B")
    Str: Column = Column("C")
    Dex: Column = Column("D")
    Con: Column = Column("E")
    Int: Column = Column("F")
    Wis: Column = Column("G")
    Cha: Column = Column("H")


def _column(DATA: list[list[str]], column: utils.Column) -> list[str]:
    """
    Entrega una columna completa (con el header)
    """
    return [row[column.excel_index()] for row in DATA]


def _first_empty_row(DATA: list[list[str]], col: utils.Column) -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de un excel
    """
    column: list[str] = _column(DATA, col)
    return len(column) + 1


def _get_id_row(DATA: list[list[str]], col: Column, id: int) -> int | None:
    """Retorna la row (index 0) de la primera fila de DATA con el id indicado."""
    id_column: list[str] = _column(DATA, col)

    try:
        return id_column.index(str(id))
    except ValueError:
        return None


def first_empty_ability_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las habilidades
    """
    global ABILITY_DATA
    return _first_empty_row(ABILITY_DATA, ABILITY_COL.Discord_id)


def first_empty_save_row() -> int:
    """
    Entrega el index (indexado a 1) de la primera fila vacía de las saves
    """
    global SAVE_DATA
    return _first_empty_row(SAVE_DATA, SAVE_COL.Discord_id)


def _get_pj_saves_raw(id: int) -> list[Tuple[int, list[str]]]:
    """
    Returna una lista de tuplas con la row (index 1) y los raw datos de todas las filas de save con el id indicado
    """
    global SAVE_DATA
    data: list[Tuple[int, list[str]]] = []
    for index_i0, row in enumerate(SAVE_DATA):
        if row[SAVE_COL.Discord_id.excel_index()] == str(id):
            data.append((index_i0 + 1, row))
    return data


class SaveRow(TypedDict):
    prof_level: str
    extra_bonus: int
    extra_descripcion: str
    row: int


def get_pj_saves(discord_id: int) -> Tuple[str | None, dict[str, SaveRow]]:
    """
    Retorna el nombre del PJ y un diccionario con las sills del pj tal que:
    {save_name: {prof_level: str, extra_bonus: int, extra_descripcion: str, row (index 1): int}}
    Las saves que no estén definidas no van en el dict (dict vacío en caso de no tener saves definidas)
    Nombre is none si el dict es vacío.
    """
    saves_raw: list[Tuple[int, list[str]]] = _get_pj_saves_raw(discord_id)
    if len(saves_raw) == 0:
        return (None, {})

    name = saves_raw[0][1][SAVE_COL.Name.excel_index()]
    saves: dict[str, SaveRow] = {}
    for index_i1, row in saves_raw:
        save_name = row[SAVE_COL.Save.excel_index()]
        prof_level = row[SAVE_COL.Proficiency.excel_index()]
        extra_bonus = utils.try_int(row[SAVE_COL.ExtraBonuses.excel_index()])
        extra_descripcion = row[SAVE_COL.ExtraDescription.excel_index()]
        row = index_i1

        saves[save_name] = {
            "prof_level": prof_level,
            "extra_bonus": extra_bonus,
            "extra_descripcion": extra_descripcion,
            "row": row,
        }
    return (name, saves)


def get_pj_save_bonus(discord_id: int, save_name: str) -> Tuple[int, str, str] | Tuple[None, None, None]:
    """Returns (bonus, prof, message) or (None, None, None)"""
    name, saves = get_pj_saves(discord_id)
    if name is None:
        return None, None, None
    name, row, stats = get_pj_abilities(discord_id)
    if name is None or row is None or stats is None:
        return None, None, None
    save_ab = [ab for sk, ab in SKILLS if sk == save_name][0]
    save_values = saves[save_name]
    prof = save_values["prof_level"]
    prof_bonus = PROF_BONUSES[prof]
    extra_bonus = save_values["extra_bonus"]
    stat_bonus = stats[save_ab]
    extra_msg = f"[Extra: {extra_bonus}]" if extra_bonus != 0 else ""
    msg = f"[{save_ab.name}: {stat_bonus}][{prof}: {prof_bonus:+}]{extra_msg}"
    return (stat_bonus + prof_bonus + extra_bonus), prof, msg


def get_pj_abilities(
    discord_id: int,
) -> Tuple[str | None, int | None, dict[Ability, int] | None]:
    """
    Retorna el nombre del PJ, la row (index 1) y un diccionario con los ability modifiers del pj tal que:
    {ability (tipo Ability): int}
    None * 3 si el PJ no ha definido sus mods
    """
    global ABILITY_DATA
    row_i0: int | None = _get_id_row(ABILITY_DATA, ABILITY_COL.Discord_id, discord_id)
    if row_i0 is None:
        return (None, None, None)

    raw_data = ABILITY_DATA[row_i0]
    name = raw_data[ABILITY_COL.Name.excel_index()]
    stats = {
        ABILITIES.Str: int(raw_data[ABILITY_COL.Str.excel_index()]),
        ABILITIES.Dex: int(raw_data[ABILITY_COL.Dex.excel_index()]),
        ABILITIES.Con: int(raw_data[ABILITY_COL.Con.excel_index()]),
        ABILITIES.Int: int(raw_data[ABILITY_COL.Int.excel_index()]),
        ABILITIES.Wis: int(raw_data[ABILITY_COL.Wis.excel_index()]),
        ABILITIES.Cha: int(raw_data[ABILITY_COL.Cha.excel_index()]),
    }
    return (name, row_i0 + 1, stats)


def update_save_row(row_index: int, data: Tuple[str, str, str, str, str, str]) -> None:
    """
    Actualiza o crea una nueva row de save.
    row_index es indexado a 1
    data debe ser tal que: [nombre_pj, discord_id, save_name, prof_level, extra_bonuses, extra_bonuses_description]
    """
    save_sheet.update([data], f"A{row_index}:F{row_index}")


def multi_update_save_row(rows_and_data: list[Tuple[int, Tuple[str, str, int, int, str]]]) -> None:
    """
    Actualiza o crea múltiples rows de save.
    row_index es indexado a 1
    data debe ser tal que: [nombre_pj, discord_id, save_name, prof_level, extra_bonuses, extra_bonuses_description]
    """
    send_batch = []
    for row_index, data in rows_and_data:
        send_batch.append({"range": f"A{row_index}:F{row_index}", "values": [data]})

    save_sheet.batch_update(send_batch)


def update_ability_row(row_index: int, data: Tuple[str, str, int, int, int, int, int, int]) -> None:
    """
    Actualiza o crea una nueva row de habilidades.
    row_index es indexado a 1
    data debe ser tal que: [nombre_pj, discord_id, STR, DEX, CON, INT, WIS, CHA]
    """
    ability_sheet.update([data], f"A{row_index}:H{row_index}")


def get_all_existing_lore_subnames(id: int | None = None) -> list[str]:
    global SAVE_DATA

    data = SAVE_DATA if id is None else [row for index, row in _get_pj_saves_raw(id)]

    save_names = _column(data, SAVE_COL.Save)

    # Se asume que todos los lores están en formato "Lore (subname)"
    lore_subnames = [save[6:-1] for save in save_names if save.startswith("Lore")]
    return lore_subnames
