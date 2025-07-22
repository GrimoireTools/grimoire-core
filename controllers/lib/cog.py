"""Cog base class and command decorator for Nextcord bots.

This module provides a base class for creating cogs in a Nextcord bot,
along with a decorator for standardizing command definitions.
It includes a setup function to register all commands with the bot instance.
"""

from collections.abc import Callable
from nextcord import Interaction, SlashApplicationCommand, slash_command
import functools
from typing import Any
from nextcord.ext import commands

from .utils import CRI_GUILD_ID, log_command, try_command


class Cog(commands.Cog):
    """Base class for creating cogs in a Nextcord bot."""

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @classmethod
    def setup(cls, client: commands.Bot) -> None:
        """Set up the cog by adding it to the bot instance."""
        client.add_cog(cls(client))


def standard_command(description: str) -> Callable[..., SlashApplicationCommand]:
    """Standardize command definitions with a description and logging."""
    if len(description) > 100:
        raise ValueError(f"Description must be less than 100 characters, length is {len(description)}: '{description}'")

    def decorator(func: Any) -> SlashApplicationCommand:
        @slash_command(description=description, guild_ids=[CRI_GUILD_ID])
        @log_command
        @try_command
        @functools.wraps(func)
        async def wrapped(self: Any, interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
            return await func(self, interaction, *args, **kwargs)

        return wrapped

    return decorator
