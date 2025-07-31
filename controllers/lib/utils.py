"""Utility functions and classes for the Costilla Bot project."""

import functools
from math import ceil
from typing import Any, Self
from gspread.exceptions import APIError
from nextcord import SlashOption, Interaction
from loguru import logger
from typing import TypeVar

from .varenv import get_var

CRI_GUILD_ID = int(get_var("GUILD_ID"))
default_user_option = SlashOption(
    name="usuario-target",
    description="Usuario al que se le aplica el comando",
    required=False,
    default=None,
)


class DataNotFoundError(Exception):
    """Custom exception for data not found in the sheet."""

    pass


class Column(str):
    """Represents a column in a spreadsheet."""

    def excel_index(self: Self) -> int:
        """
        Entrega el indice (indexado a 0) de la letra de la columna.

        Ejemplos:
        - A -> 0
        - C -> 2
        - AA -> 26.
        """
        return column_to_num(self)


class CoinsList(list[int]):
    """A list of coins in the order: pp, gp, sp, cp."""

    def __init__(self, *args: int) -> None:
        """
        Crea una lista de monedas a partir de 4 enteros.

        Los enteros son la cantidad de monedas de cada tipo, en orden:
        - pp
        - gp
        - sp
        - cp.
        """
        super().__init__(args)
        if len(args) != 4:
            raise ValueError("CoinsList must have 4 elements")
        self.pp = args[0]
        self.gp = args[1]
        self.sp = args[2]
        self.cp = args[3]

    def __repr__(self) -> str:
        """Return a string representation of the CoinsList."""
        return f"CoinsList({self.pp}, {self.gp}, {self.sp}, {self.cp})"

    def pretty_print(self) -> str:
        """Xpp, Xgp, Xsp, Xcp."""
        return f"{self.pp}pp, {self.gp}gp, {self.sp}sp, {self.cp}cp"

    def total(self) -> float:
        """Calcula el dinero total en gp."""
        return self.pp * 10 + self.gp + self.sp * 0.1 + self.cp * 0.01


def sign(num: int | float) -> int:
    """Return the sign of a number."""
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
    """Parse a string to a float, replacing commas with dots."""
    rnum = num.replace(",", ".")
    try:
        return float(rnum)
    except ValueError as err:
        raise ValueError(f"{num} no es un número válido") from err


def gp_to_coin_list(num: float) -> CoinsList:
    """Given an amount of gold, returns its representation in coins, minimizing the total amount of coins."""
    num = (1 if num >= 0 else -1) * round(abs(float(num)) * 100)

    pp = num // 1000
    gp = num % 1000 // 100
    sp = num % 100 // 10
    cp = num % 10

    return CoinsList(pp, gp, sp, cp)


def check_results(dc: int, result: int, dice: int) -> int:
    """
    Return the degree of success of a check based on the DC, result, and dice.

    Given a DC, a dice result (with bonuses), and the unmodified result of the dice,
    return the degree of success of the check, from 0 (crit fail) to 3 (crit success).
    """
    check_results = {
        -1: 0,
        0: 0,  # crit fail
        1: 1,  # fail
        2: 2,  # success
        3: 3,  # crit success
        4: 3,
    }
    if result >= dc + 10:
        success_rate = 3
    elif result >= dc:
        success_rate = 2
    elif result > dc - 10:
        success_rate = 1
    else:
        success_rate = 0

    success_rate += 1 if dice == 20 else 0  # nat20
    success_rate -= 1 if dice == 1 else 0  # nat1

    return check_results[success_rate]


def result_name(result: int) -> str:
    """Return the string name representation of the success degree, given a success value from 0 to 3."""
    return ["fallo crítico", "fallo", "éxito", "éxito crítico"][result]


def pay_priority(coins: list[int], paid_amt: float) -> list[int]:
    """Calculate the optimal way to pay a given amount using available coins.

    Given a list of coins and an amount to pay, determine the change in each coin type
    to minimize the number of coins used, prioritizing higher denominations.

    Args:
        coins (list[int]): List of available coins in the order [pp, gp, sp, cp, ...].
        paid_amt (float): Amount to pay in gold pieces (gp).

    Returns:
        list[int]: List of integers representing the change in each coin type after payment.

    Raises:
        ValueError: If the coins list does not have the expected length.
    """
    # calcula la diferencia (lo que hay que restarle al dinero original) para pagar paid_amt
    price = gp_to_coin_list(paid_amt)
    # pagamos de las monedas mas caras a las mas baratas
    old = [int(float(x)) for x in coins]
    vals = [10, 10, 10, 10]

    resta = [old[i] - price[i] for i in range(5)]

    # convierte monedas pequeñas en monedas grandes
    for i in range(4):
        if resta[i] < 0:
            resta[i + 1] += resta[i] * vals[i]
            resta[i] = 0

    # convierte las monedas grandes en monedas pequeñas
    for j in range(4, 0, -1):
        if resta[j] < 0:
            cambio = ceil(-resta[j] / vals[j - 1])
            resta[j] += cambio * vals[j - 1]
            resta[j - 1] -= cambio

    return [resta[i] - old[i] for i in range(5)]


def num_to_column(column_int: int) -> str:
    """
    Entrega la letra de un numero (indexado a 1).

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
    """Try to convert a string to an integer, returning 0 if it fails."""
    try:
        return int(val)
    except ValueError:
        return 0


def log_command(func: Any) -> Any:
    """Wrap a function in a decorator to log command calls."""

    @functools.wraps(func)
    @logger.catch
    async def logged_command(self: Any, interaction: Interaction, *args: Any, **kwargs: Any) -> None:
        user = interaction.user
        if user is not None:
            logger.info(f"[{func.__name__}] called by {user.name} ({user.id}).")
        else:
            logger.info(f"[{func.__name__}] called by null user.")
        logger.debug(f"[{func.__name__}] called with {kwargs}.")

        await func(self, interaction, *args, **kwargs)

    return logged_command


def log_command_not_cog(func: Any) -> Any:
    """Wrap a function in a decorator to log command calls without a Cog context."""

    @functools.wraps(func)
    @logger.catch
    async def logged_command(interaction: Interaction, *args: Any, **kwargs: Any) -> None:
        user = interaction.user
        if user is not None:
            logger.info(f"[{func.__name__}] called by {user.name} ({user.id}).")
        else:
            logger.info(f"[{func.__name__}] called by null user.")
        logger.debug(f"[{func.__name__}] called with {kwargs}.")
        await func(interaction, *args, **kwargs)

    return logged_command


def try_command(func: Any) -> Any:
    """Wrap a function in a decorator to handle exceptions gracefully."""

    @functools.wraps(func)
    async def try_command_func(self: Any, interaction: Interaction, *args: Any, **kwargs: Any) -> None:
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
            await interaction.followup.send(f"Google API Error: {e!s}. Prueba de nuevo en unos minutos.")

    return try_command_func


def column_to_num(column: str) -> int:
    """
    Entrega el indice (indexado a 0 de la letra de la columna).

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
