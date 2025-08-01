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
from nextcord import ForumChannel, ForumTag, Guild, Interaction, Member, SlashOption, TextChannel, Thread
from controllers.lib.utils import StopError, check_narrator, not_none, default_user_option
from controllers.lib.cog import Cog, standard_command

from controllers.pjs_controller import get_cached_name
import re
import asyncio

from controllers.roles_controller import pretty_roles

MISSION_CHANNEL_ID = 1203377141799063662
MISSION_FORUM_ID = 1203371926438027314
INFORMES_FORUM_ID = 1265011561895035043

MISSION_FORUM_GM_TAGS: dict[int, str] = {
    393913641834905601: "Argi",
    137000318440439808: "Edo",
    380098969709314054: "Luciano",
    137054851791060992: "Cris",
    779413237565227051: "Alonso",
    190073840607559680: "Fran",
    334582584967430144: "Taco",
    329424775678001152: "Jua",
    360212346137739265: "Tommy",
    952634365484077116: "Nilo",
    302902786494824449: "Axl",
}


class AnnouncementsCommands(Cog):
    """Discord cog for managing mission announcements and participant tracking.

    This cog handles the creation of mission notices, manages participant
    reactions, and maintains forum threads for mission coordination.

    Attributes:
        _message_locks: Dictionary to prevent race conditions during message processing.
    """

    _message_locks: dict[int, asyncio.Lock]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._message_locks = {}

    async def _process_reaction(
        self: Self, payload: nextcord.RawReactionActionEvent
    ) -> (
        tuple[
            nextcord.Guild,
            nextcord.Member,
            nextcord.channel.TextChannel,
        ]
        | tuple[None, None, None]
    ):
        """
        Process a reaction event to determine if it should be handled.

        Checks if the reaction is in the correct channel and identifies the user
        and channel involved. If the reaction is from the bot itself or in the
        wrong channel, it returns None. Otherwise, it returns a tuple of
        (guild, user, channel).
        """
        if payload.user_id == not_none(self.client.user).id:
            return None, None, None
        if payload.channel_id != MISSION_CHANNEL_ID:
            return None, None, None
        guild = self.client.get_guild(not_none(payload.guild_id))
        if not guild:
            return None, None, None
        user = guild.get_member(payload.user_id)
        if not user:
            try:
                user = await guild.fetch_member(payload.user_id)
            except nextcord.NotFound:
                # Fallback to getting user from client cache
                user = self.client.get_user(payload.user_id)
                if not user or not isinstance(user, nextcord.Member):
                    print(f"User not found anywhere: user_id={payload.user_id}, guild_id={payload.guild_id}")
                    return None, None, None
        channel = guild.get_channel(payload.channel_id)
        if not channel or not isinstance(channel, nextcord.TextChannel):
            return None, None, None
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
        ),
        duration: str = SlashOption("duración", "Duración de la mesa", default="4-5 horas"),
        players: str = "4-5",
        user: Member = default_user_option,  # type: ignore[assignment]
    ) -> Any:
        """Generate a mission notice."""
        # Check if user has the required role
        narrator = check_narrator(interaction.user)
        if user is not None:
            narrator = check_narrator(user)

        print(f"Mission notice requested by {narrator.name} ({narrator.id})")
        # Get the mission channel and forum
        mission_channel, mission_forum, informes_forum = get_channels(interaction)

        mission_name = f"T{turn} Lvl {tier}: {mission_name}"

        # Create forum thread
        gm_tag, tier_tag = get_tags(mission_forum, narrator, tier)
        if not gm_tag or not tier_tag:
            raise StopError(f"Could not find a valid {'GM' if not gm_tag else 'tier'} tag.")

        announcement = mission_announcement(description, tags, mission_name, narrator, players, duration, disponibility)

        thread = await post_forum_announcement(
            interaction, mission_name, announcement, tags=[gm_tag, tier_tag], forum=mission_forum
        )
        if thread is None:
            raise StopError("Could not create the forum thread for the mission.")
        announcement += f"\nForo: {thread.mention}"

        gm_tag, tier_tag = get_tags(informes_forum, narrator, tier)
        if not gm_tag or not tier_tag:
            raise StopError(f"Could not find a valid {'GM' if not gm_tag else 'tier'} tag.")
        await post_forum_announcement(
            interaction, mission_name, announcement, tags=[gm_tag, tier_tag], forum=informes_forum
        )

        # Create the announcement message
        await mission_channel.send(content=announcement)
        await interaction.followup.send(f"Misión anunciada: {mission_name}. Puedes ver el hilo en {thread.mention}.")

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
        guild, user, channel = await self._process_reaction(payload)
        if not guild or not user or not channel:
            return

        async def process_add() -> None:
            message = await channel.fetch_message(payload.message_id)
            print(f"Reaction added by {user.name} ({user.id}) to message {message.id}")

            if message.author == self.client.user and message.content.startswith("# __T"):
                content = message.content

                if user.mention not in content:
                    content = add_participant(content, user, payload.emoji.name or "❓")
                    await message.edit(content=content)
                    # Extract thread mention from the content and add user to it
                    thread = extract_thread(guild, content)
                    if thread:
                        await thread.add_user(user)
                    # Add user to report thread if it exists
                    name = extract_mission_name(content)
                    if name:
                        report_thread = find_report_thread(name, guild)
                        if report_thread:
                            await report_thread.add_user(user)

        await self._process_message_safely(payload.message_id, process_add)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent) -> None:
        """Handle reaction removed from mission announcement messages."""
        guild, user, channel = await self._process_reaction(payload)
        if not guild or not user or not channel:
            return

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


def add_participant(content: str, user: Member, emoji: str) -> str:
    """Add a participant to the mission announcement content."""
    if "**Participantes:**" not in content:
        content += "\n**Participantes:**"

    content += f"\n- {emoji} {get_cached_name(user.id)} ({user.mention}): {pretty_roles(user.id)}"
    return content


def extract_thread(guild: Guild, content: str) -> Thread | None:
    """Extract the thread ID from the content of an announcement."""
    match = re.search(r"<#(\d+)>", content)
    if match:
        thread_id = int(match.group(1))
        thread = guild.get_thread(thread_id)
        if thread:
            return thread
    return None


def _find_tag(tags: list[ForumTag], name: str) -> ForumTag | None:
    """Find a tag by name in the list of tags."""
    for tag in tags:
        if tag.name.lower() == name.lower():
            return tag
    return None


def get_tags(forum: ForumChannel, gm: Member, tier: str) -> tuple[ForumTag | None, ForumTag | None]:
    """Get the available tags from a forum channel."""
    tag_list = forum.available_tags
    gm_tag = _find_tag(tag_list, MISSION_FORUM_GM_TAGS.get(gm.id, "GM"))
    tier_tag = _find_tag(tag_list, f"tier {tier.lower()}")

    return (gm_tag, tier_tag)


async def post_forum_announcement(
    interaction: Interaction,
    name: str,
    announcement: str,
    tags: list[ForumTag],
    forum: ForumChannel,
) -> nextcord.Thread | None:
    """Post an announcement in the specified forum with the given tags."""
    if not tags:
        return await interaction.followup.send("Error: No valid tags provided for the announcement.")
    # Create a forum thread with the announcement
    thread = await forum.create_thread(
        name=name,
        content=announcement,
        applied_tags=tags,
    )
    await thread.add_user(not_none(interaction.user))
    return thread


def mission_announcement(
    description: str,
    tags: str,
    mission_name: str,
    narrator: Member,
    players: str,
    duration: str,
    disponibility: str,
) -> str:
    """Return the description of the mission announcement."""
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []

    # Ensure description is wrapped in a code block if not already
    desc = description.strip()
    desc = f"```ansi\n{desc}\n```" if not (desc.startswith("```") and desc.endswith("```")) else desc

    return f"""# __{mission_name}__
{desc}
Narrador: {narrator.mention}
Tamaño de party: {players}
Duración: {duration}
Disponibilidad: {disponibility}
Tags: {", ".join(tag_list) if tag_list else "Ninguno"}

"""


def extract_mission_name(content: str) -> str | None:
    """Extract the mission name from the content."""
    match = re.search(r"# __([^#]+)__", content)
    if match:
        return match.group(1).strip()
    return None


def find_report_thread(title: str, guild: nextcord.Guild) -> nextcord.Thread | None:
    """Find a report thread by title in the specified forum."""
    forum = guild.get_channel(INFORMES_FORUM_ID)
    if not forum or not isinstance(forum, ForumChannel):
        raise StopError("The reports forum is not a valid forum channel.")
    for thread in forum.threads:
        if title in thread.name:
            return thread
    return None


def get_channels(interaction: Interaction) -> tuple[TextChannel, ForumChannel, ForumChannel]:
    """Get the mission channel and forums for mission announcements."""
    guild = not_none(interaction.guild)
    mission_channel = guild.get_channel(MISSION_CHANNEL_ID)
    mission_forum = guild.get_channel(MISSION_FORUM_ID)
    informes_forum = guild.get_channel(INFORMES_FORUM_ID)
    if not mission_channel or not mission_forum or not informes_forum:
        raise StopError("Could not find mission channel, reports from or mission forum.")
    if not isinstance(mission_forum, ForumChannel):
        raise StopError("The mission forum is not a valid forum channel.")
    if not isinstance(informes_forum, ForumChannel):
        raise StopError("The reports forum is not a valid forum channel.")
    if not isinstance(mission_channel, nextcord.TextChannel):
        raise StopError("The mission channel is not a valid text channel.")
    return mission_channel, mission_forum, informes_forum
