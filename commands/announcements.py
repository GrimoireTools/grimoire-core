"""Mission announcement management for Discord bot.

This module provides commands and event handlers for creating and managing
mission announcements in a Discord server. It includes functionality for
generating mission notices, creating forum threads, and handling participant
reactions.

Classes:
    AnnouncementsCommands: Cog for handling mission announcement commands.
"""

from typing import Any, Self
from collections.abc import Callable, Awaitable

import nextcord
from nextcord import ForumChannel, SlashOption
from controllers.lib.utils import not_none
from controllers.lib.cog import Cog, standard_command

from controllers.pjs_controller import get_cached_name
import re
import asyncio

MISSION_CHANNEL_ID = 1203377771812888656
MISSION_FORUM_ID = 1268419186149818399
MASTERS_ROLE_ID = 1163525259962626219


class AnnouncementsCommands(Cog):
    """Discord cog for managing mission announcements and participant tracking.

    This cog handles the creation of mission notices, manages participant
    reactions, and maintains forum threads for mission coordination.

    Attributes:
        _message_locks: Dictionary to prevent race conditions during message processing.
    """

    async def _process_reaction(
        self: Self, payload: nextcord.RawReactionActionEvent
    ) -> (
        tuple[
            nextcord.Guild,
            nextcord.Member | nextcord.User,
            nextcord.channel.TextChannel,
        ]
        | None
    ):
        """
        Process a reaction event to determine if it should be handled.

        Checks if the reaction is in the correct channel and identifies the user
        and channel involved. If the reaction is from the bot itself or in the
        wrong channel, it returns None. Otherwise, it returns a tuple of
        (guild, user, channel).
        """
        if payload.user_id == not_none(self.client.user).id:
            return None
        if payload.channel_id != MISSION_CHANNEL_ID:
            return None
        guild = self.client.get_guild(not_none(payload.guild_id))
        if not guild:
            return None
        user = guild.get_member(payload.user_id)
        if not user:
            try:
                user = await guild.fetch_member(payload.user_id)
            except nextcord.NotFound:
                # Fallback to getting user from client cache
                user = self.client.get_user(payload.user_id)
                if not user:
                    print(f"User not found anywhere: user_id={payload.user_id}, guild_id={payload.guild_id}")
                    return None
        channel = guild.get_channel(payload.channel_id)
        if not channel or not isinstance(channel, nextcord.TextChannel):
            return None
        return guild, user, channel

    @standard_command("Genera un aviso de misión.")
    async def mission_notice(
        self: Self,
        interaction: nextcord.Interaction,
        turn: int,
        mission_name: str,
        description: str,
        tier: str = SlashOption("tier", "tier de la misión", choices=["alto", "bajo"]),
        disponibility: str = SlashOption("disponibilidad", "Disponibilidad de la mesa"),
        tags: str = SlashOption(
            "tags",
            "tags de la misión, separados por comas (ej. 'exploración, combate')",
            default="",
        ),
        duration: str = SlashOption("duración", "Duración de la mesa", default="4-5 horas"),
        players: str = "4-5",
    ) -> Any:
        """Generate a mission notice."""
        # Check if user has the required role
        user: nextcord.Member | nextcord.User = not_none(interaction.user)
        if not isinstance(user, nextcord.Member) or not any(role.id == MASTERS_ROLE_ID for role in user.roles):
            await interaction.followup.send("You don't have permission to create mission notices.", ephemeral=True)
            return

        narrator = not_none(interaction.user)
        print(f"Mission notice requested by {narrator.name} ({narrator.id})")
        # Get the mission channel and forum
        guild = not_none(interaction.guild)
        mission_channel = guild.get_channel(MISSION_CHANNEL_ID)
        mission_forum = guild.get_channel(MISSION_FORUM_ID)
        if not mission_channel or not mission_forum:
            await interaction.followup.send("Error: Could not find mission channel or forum.", ephemeral=True)
            return
        if not isinstance(mission_forum, ForumChannel):
            await interaction.followup.send("Error: The mission forum is not a valid forum channel.", ephemeral=True)
            return
        if not isinstance(mission_channel, nextcord.TextChannel):
            await interaction.followup.send(
                "Error: The mission channel is not a valid text channel.",
                ephemeral=True,
            )
            return
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        announcement = f"""# __T{turn} Lvl {tier}: *{mission_name}*__
```ansi
{description}
```
Narrador: {narrator.mention}
Tamaño de party: {players}
Duración: {duration}
Disponibilidad: {disponibility}
Tags: {", ".join(tag_list) if tag_list else "Ninguno"}

"""
        # Create forum thread
        forum_tags = mission_forum.available_tags

        thread = await mission_forum.create_thread(
            name=f"T{turn} {tier.title()}: {mission_name}",
            content=announcement,
            applied_tags=forum_tags[0:2],  # Use first two tags as an example
        )
        await thread.add_user(narrator)
        announcement += f"Foro: {thread.mention}\n\n**Participantes:**"

        # Create the announcement message
        _message = await mission_channel.send(
            content=announcement,
        )
        await interaction.followup.send(f"Misión anunciada: {mission_name}. Puedes ver el hilo en {thread.mention}.")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._message_locks = {}

    async def _process_message_safely(self, message_id: int, processor_func: Callable[[], Awaitable[None]]) -> None:
        """Process message with lock to avoid race conditions."""
        if message_id not in self._message_locks:
            self._message_locks[message_id] = asyncio.Lock()

        lock = self._message_locks[message_id]

        async with lock:
            try:
                await processor_func()
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent) -> None:
        """Handle reaction added to mission announcement messages."""
        process = await self._process_reaction(payload)
        if not process:
            return
        guild, user, channel = process

        async def process_add() -> None:
            message = await channel.fetch_message(payload.message_id)
            print(f"Reaction added by {user.name} ({user.id}) to message {message.id}")

            if message.author == self.client.user and message.content.startswith("# __T"):
                content = message.content
                if "**Participantes:**" not in content:
                    content += "\n**Participantes:**"

                if user.mention not in content:
                    content += f"\n- {payload.emoji} {get_cached_name(user.id)} {user.mention}"
                    await message.edit(content=content)
                    # Extract thread mention from the content and add user to it
                    thread_mention_match = re.search(r"<#(\d+)>", content)
                    if thread_mention_match:
                        thread_id = int(thread_mention_match.group(1))
                        thread = guild.get_thread(thread_id)
                        if thread:
                            await thread.add_user(user)

        await self._process_message_safely(payload.message_id, process_add)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent) -> None:
        """Handle reaction removed from mission announcement messages."""
        process = await self._process_reaction(payload)
        if not process:
            return
        guild, user, channel = process

        async def process_remove() -> None:
            message = await channel.fetch_message(payload.message_id)
            print(f"Reaction removed by {user.name} ({user.id}) from message {message.id}")

            if message.author == self.client.user and message.content.startswith("# __T"):
                content = message.content
                if user.mention in content:
                    lines = content.split("\n")
                    lines = [line for line in lines if user.mention not in line or line.strip().startswith("Narrador:")]
                    content = "\n".join(lines)
                    await message.edit(content=content)

        await self._process_message_safely(payload.message_id, process_remove)
