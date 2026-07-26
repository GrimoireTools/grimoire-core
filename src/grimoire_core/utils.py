import functools
from typing import Any, Self, TypeVar

from gspread.exceptions import APIError
from loguru import logger
from nextcord import Interaction, SlashOption, Member, User

from grimoire_core.varenv import get_env

CRI_GUILD_ID = int(get_env("GUILD_ID"))
default_user_option = SlashOption(
    name="usuario-target",
    description="Usuario al que se le aplica el comando",
    required=False,
    default=None,
)


class DataNotFoundError(Exception):
    pass


class StopError(Exception):
    """Custom exception to stop the execution of a command."""

    pass


class Column(str):
    def excel_index(self: Self) -> int:
        """
        Entrega el indice (indexado a 0) de la letra de la columna
        Ejemplos:
        - A -> 0
        - C -> 2
        - AA -> 26.
        """
        return column_to_num(self)


def sign(num: int | float) -> int:
    return 1 if num >= 0 else -1


T = TypeVar("T")


class NoneError(Exception):
    """Custom exception for None values."""

    pass


def not_none(val: T | None) -> T:
    """Return the value if not None, otherwise raises ValueError."""
    if val is None:
        raise NoneError("Value cannot be None")
    return val


def parse_float_arg(num: str) -> float:
    rnum = num.replace(",", ".")
    try:
        return float(rnum)
    except ValueError:
        raise ValueError(f"{num} no es un número válido")


def num_to_column(column_int: int) -> str:
    """
    Entrega la letra de un numero (indexado a 1)
    Ejemplos:
    - 1 -> A
    - 3 -> C
    - 27 -> AA.
    """
    if column_int <= 0:
        raise ValueError("Column must be 1 or higher.")
    start_index = 1  # it can start either at 0 or at 1
    letter = ""
    while column_int > 25 + start_index:
        letter += chr(65 + int((column_int - start_index) / 26) - 1)
        column_int = column_int - (int((column_int - start_index) / 26)) * 26
    letter += chr(65 - start_index + (int(column_int)))
    return letter


def try_int(val: str) -> int:
    try:
        return int(val)
    except ValueError:
        return 0


def log_command(func):
    @functools.wraps(func)
    @logger.catch
    async def logged_command(self: Any, interaction: Interaction, *args, **kwargs) -> None:
        user = interaction.user
        if user is not None:
            logger.info(f"[{func.__name__}] called by {user.name} ({user.id}).")
        else:
            logger.info(f"[{func.__name__}] called by null user.")
        logger.debug(f"[{func.__name__}] called with {kwargs}.")

        await func(self, interaction, *args, **kwargs)

    return logged_command


def log_command_not_cog(func):
    @functools.wraps(func)
    @logger.catch
    async def logged_command(interaction: Interaction, *args, **kwargs) -> None:
        user = interaction.user
        if user is not None:
            logger.info(f"[{func.__name__}] called by {user.name} ({user.id}).")
        else:
            logger.info(f"[{func.__name__}] called by null user.")
        logger.debug(f"[{func.__name__}] called with {kwargs}.")
        await func(interaction, *args, **kwargs)

    return logged_command


def try_command(func):
    @functools.wraps(func)
    async def try_command_func(self: Any, interaction: Interaction, *args, **kwargs):
        try:
            await interaction.response.defer()
            if interaction.user is None:
                return await interaction.followup.send("Error: Null user")
            return await func(self, interaction, *args, **kwargs)
        except DataNotFoundError as e:
            await interaction.followup.send(f"DataNotFoundError: {e}")
        except NoneError:
            await interaction.followup.send("None Error: not_none found None value")
        except APIError as e:
            await interaction.followup.send(f"API Error: {e!s}")

    return try_command_func


def column_to_num(column: str) -> int:
    """
    Entrega el indice (indexado a 0 de la letra de la columna)
    Ejemplos:
    - A -> 0
    - C -> 2
    - AA -> 26.
    """
    letters: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
    num: int = 0
    for letter in column.lower():
        if letter not in letters:
            raise ValueError("Column must have only roman alphabet characters.")
        num *= len(letters)
        num += letters.index(letter) + 1

    return num - 1


MASTERS_ROLE_ID = 1163525259962626219


def check_narrator(user: Member | User | None) -> Member:
    """Check if the interaction user is a narrator."""
    narrator = not_none(user)
    if not isinstance(narrator, Member):
        raise StopError("You must be a member of the server to create mission notices.")
    if not any(role.id == MASTERS_ROLE_ID for role in narrator.roles):
        raise StopError("You don't have the narrator role.")
    return narrator
