from nextcord import Interaction, slash_command
import functools
from typing import Any
from nextcord.ext import commands

from .utils import CRI_GUILD_ID, log_command, try_command


class Cog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @classmethod
    def setup(cls, client: commands.Bot) -> None:
        client.add_cog(cls(client))


def standard_command(description: str):
    def decorator(func):
        @slash_command(description=description, guild_ids=[CRI_GUILD_ID])
        @log_command
        @try_command
        @functools.wraps(func)
        async def wrapped(self: Any, interaction: Interaction, *args, **kwargs):
            return await func(self, interaction, *args, **kwargs)

        return wrapped

    return decorator
