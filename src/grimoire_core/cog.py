"""Utility class for nextcord, providing a base Cog class and decorators for standard commands."""

import functools
from collections.abc import Awaitable, Callable
from typing import Any, Concatenate, ParamSpec, TypeVar

from gspread.exceptions import APIError
from loguru import logger
from nextcord import Interaction, SlashApplicationCommand, slash_command
from nextcord.ext import commands

from grimoire_core.utils import CRI_GUILD_ID, DataNotFoundError, NoneError


class Cog(commands.Cog):
    """Base class for all Cogs in the bot.

    Call setup() to add the Cog to the bot.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @classmethod
    def setup(cls, client: commands.Bot) -> None:
        """Add the Cog to the bot."""
        client.add_cog(cls(client))


P = ParamSpec("P")
R = TypeVar("R")

type CommandFunc[**P] = Callable[
    Concatenate[Any, Interaction, P],
    Awaitable[Any],
]

type InteractionFunc[**P] = Callable[
    Concatenate[Interaction, P],
    Awaitable[Any],
]

type AnyCommand = Callable[..., Awaitable[Any]]


def log_command(func: AnyCommand) -> AnyCommand:
    """Decorator to log the execution of a command function."""

    @functools.wraps(func)
    @logger.catch
    async def logged_command(*args: Any, **kwargs: Any) -> Any:
        interaction = kwargs.get("interaction")

        if interaction is None:
            for arg in args:
                if isinstance(arg, Interaction):
                    interaction = arg
                    break

        if interaction is not None:
            user = interaction.user
            if user is not None:
                logger.info(f"[{func.__name__}] called by {user.name} ({user.id}).")
            else:
                logger.info(f"[{func.__name__}] called by null user.")

        logger.debug(f"[{func.__name__}] called with {kwargs}.")

        return await func(*args, **kwargs)

    return logged_command


def try_command(func: CommandFunc[P]) -> CommandFunc[P]:
    """Handle common command exceptions."""

    @functools.wraps(func)
    async def try_command_func(
        self: Any,
        interaction: Interaction,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
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


def standard_command(description: str) -> Callable[[CommandFunc[P]], SlashApplicationCommand]:
    """Define a decorator for standard commands.

    Sets the command to be a slash command, logs the command, and wraps the function with error handling.
    """
    if len(description) > 100:
        raise ValueError(f"Description must be less than 100 characters, length is {len(description)}: '{description}'")

    def decorator(func: CommandFunc[P]) -> SlashApplicationCommand:
        """Wrap the function with the standard command decorators."""

        @slash_command(description=description, guild_ids=[CRI_GUILD_ID])
        @log_command
        @try_command
        @functools.wraps(func)
        async def wrapped(self: Any, interaction: Interaction, *args: P.args, **kwargs: P.kwargs) -> Any:
            return await func(self, interaction, *args, **kwargs)

        return wrapped

    return decorator
