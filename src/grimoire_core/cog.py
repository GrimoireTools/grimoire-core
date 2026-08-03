"""Utility class for nextcord, providing a base Cog class and decorators for standard commands."""

import functools
from collections.abc import Awaitable, Callable
from typing import Any, Concatenate, ParamSpec

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

type CommandFunc[**P] = Callable[
    Concatenate[Any, Interaction, P],
    Awaitable[Any],
]


type AnyCommand = Callable[..., Awaitable[Any]]


async def send_error(interaction: Interaction, message: str) -> Any:
    """Send an error message using the correct interaction response method."""
    if interaction.response.is_done():
        await interaction.followup.send(message)
    else:
        await interaction.response.send_message(message)


def find_interaction(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Interaction | None:
    """Find the Interaction argument in a command call."""
    interaction = kwargs.get("interaction")

    if isinstance(interaction, Interaction):
        return interaction

    for arg in args:
        if isinstance(arg, Interaction):
            return arg

    return None


def log_command(func: AnyCommand) -> AnyCommand:
    """Log command execution."""

    @functools.wraps(func)
    async def logged_command(*args: Any, **kwargs: Any) -> Any:
        interaction = kwargs.get("interaction")

        if interaction is None:
            interaction = next(
                (arg for arg in args if isinstance(arg, Interaction)),
                None,
            )

        if interaction is not None:
            user = interaction.user
            if user is not None:
                logger.info(f"[{func.__name__}] called by {user.name} ({user.id}).")
            else:
                logger.info(f"[{func.__name__}] called by null user.")

        logger.debug(f"[{func.__name__}] called with {kwargs}.")

        return await func(*args, **kwargs)

    return logged_command


def try_command(func: AnyCommand) -> AnyCommand:
    """Handle common command exceptions."""

    @functools.wraps(func)
    @logger.catch
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        interaction = find_interaction(args, kwargs)

        if interaction is None:
            raise RuntimeError("Command has no Interaction argument")

        try:
            return await func(*args, **kwargs)

        except DataNotFoundError as e:
            await send_error(interaction, f"DataNotFoundError: {e}")

        except NoneError:
            await send_error(interaction, "None Error: not_none found None value")

        except APIError as e:
            await send_error(interaction, f"API Error: {e!s}")
        except Exception:
            logger.exception("Unhandled command error")
            await send_error(
                interaction,
                "An unexpected error occurred.",
            )

    return wrapped


def defer_command(func: AnyCommand) -> AnyCommand:
    """Defer the interaction response before executing the command."""

    @functools.wraps(func)
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        interaction = find_interaction(args, kwargs)

        if interaction is None:
            raise RuntimeError("Command has no Interaction argument")

        await interaction.response.defer()

        return await func(*args, **kwargs)

    return wrapped


def command_wrapper(func: CommandFunc[P]) -> CommandFunc[P]:
    """Apply standard command middleware."""
    return log_command(defer_command(try_command(func)))


def standard_command(description: str) -> Callable[[CommandFunc[P]], SlashApplicationCommand]:
    """Define a standard slash command."""
    if len(description) > 100:
        raise ValueError(f"Description must be less than 100 characters, length is {len(description)}: '{description}'")

    def decorator(func: CommandFunc[P]) -> SlashApplicationCommand:
        return slash_command(
            description=description,
            guild_ids=[CRI_GUILD_ID],
        )(command_wrapper(func))

    return decorator
