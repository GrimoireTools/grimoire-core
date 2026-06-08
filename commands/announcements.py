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
from nextcord import ForumChannel, ForumTag, Guild, Interaction, Member, Message, SlashOption, TextChannel, Thread
from controllers.lib.utils import StopError, check_narrator, not_none, default_user_option
from controllers.lib.cog import Cog, standard_command

from controllers.pjs_controller import get_cached_name
import re
import asyncio
from loguru import logger

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
    190073840607559680: "Emi",
    334582584967430144: "Taco",
    329424775678001152: "Jua",
    360212346137739265: "Tommy",
    952634365484077116: "Nilo",
    302902786494824449: "Axl",
    801992897045463070: "Tolquiem",
    270690478599438336: "Quemares"

}
"""ID de cada master narrador y su tag en el foro de misiones."""


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
                    logger.warning(f"User not found anywhere: user_id={payload.user_id}, guild_id={payload.guild_id}")
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
        players: str,
        tier: str = SlashOption("tier", "tier de la misión", choices=["Alto", "Bajo"]),
        disponibility: str = SlashOption("disponibilidad", "Disponibilidad de la mesa"),
        tags: str = SlashOption(
            "tags",
            "tags de la misión, separados por comas (ej. 'exploración, combate')",
        ),
        duration: str = SlashOption("duración", "Duración de la mesa", default="4-5 horas"),
        user: Member = default_user_option,  # type: ignore[assignment]
    ) -> Any:
        """Generate a mission notice."""
        # Check if user has the required role
        narrator = check_narrator(interaction.user)
        if user is not None:
            narrator = check_narrator(user)
        # Get the message being responded to, if any
        try:
            mission_channel, _, _ = get_channels(interaction)
        except Exception as e:
            raise StopError(f"No se pudo obtener el mensaje de descripción: {e}") from e

        logger.info(f"Mission notice requested by {narrator.name} ({narrator.id})")
        # Get the mission channel and forum
        mission_channel, mission_forum, informes_forum = get_channels(interaction)

        mission_name = f"T{turn} Lvl {tier}: {mission_name}"
        await interaction.followup.send(
            f"Generando aviso de misión: {mission_name} en {mission_channel.mention}...\n"
            f"Por favor, responde al mensaje con la descripción de la misión dentro de los siguientes 2 minutos."
        )

        def check_response(interaction: nextcord.Interaction) -> None:
            async def wait_for_response() -> None:
                og_msg = await interaction.original_message()
                try:
                    response: Message = await self.client.wait_for(
                        "message",
                        timeout=120,
                        check=lambda m: (
                            m.channel == interaction.channel
                            and m.author == interaction.user
                            and m.reference is not None
                            and m.reference.message_id == og_msg.id
                        ),
                    )
                    description = response.content.strip()
                    if not description:
                        await interaction.followup.send("La descripción no puede estar vacía.")
                        return

                    announcement = mission_announcement(
                        description, tags, mission_name, narrator, players, duration, disponibility
                    )
                    announcement, report_thread = await create_threads(
                        interaction, mission_name, tier, narrator, mission_forum, informes_forum, announcement
                    )

                    # Create the announcement message
                    await mission_channel.send(content=announcement)
                    await response.reply(
                        f"Misión anunciada: {mission_name}. Puedes ver el hilo en {report_thread.mention}."
                    )
                except TimeoutError:
                    await og_msg.reply("No se recibió respuesta dentro del período de espera.")
                except StopError as e:
                    await og_msg.reply(f"Error: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error in mission_notice: {e}")
                    await og_msg.reply(f"Error inesperado: {e}")

            asyncio.create_task(wait_for_response())  # noqa: RUF006

        check_response(interaction)

    async def _process_message_safely(self, message_id: int, processor_func: Callable[[], Awaitable[None]]) -> None:
        """Process message with lock to avoid race conditions."""
        if message_id not in self._message_locks:
            self._message_locks[message_id] = asyncio.Lock()

        lock = self._message_locks[message_id]

        async with lock:
            try:
                await processor_func()
            except Exception as e:
                logger.warning(f"Error processing message {message_id}: {e}")

    @standard_command("Edita un anuncio de misión")
    async def edit_notice(
        self,
        interaction: Interaction,
        message_id: int,
        turn: int | None = SlashOption("turn", "número de turno", default=None),
        mission_name: str | None = SlashOption("mission_name", "nombre de la misión", default=None),
        players: str | None = SlashOption("players", "tamaño de la party", default=None),
        tier: str | None = SlashOption("tier", "tier de la misión", choices=["Alto", "Bajo"], default=None),
        disponibility: str | None = SlashOption("disponibilidad", "Disponibilidad de la mesa", default=None),
        tags: str | None = SlashOption(
            "tags",
            "tags de la misión, separados por comas (ej. 'exploración, combate')",
            default=None,
        ),
        duration: str | None = SlashOption("duración", "Duración de la mesa", default=None),
        user: Member = default_user_option,  # type: ignore[assignment]
    ) -> None:
        """Edits an existing mission announcement and corresponding threads."""
        # Check if user has the required role
        narrator = check_narrator(interaction.user)
        if user is not None:
            narrator = check_narrator(user)

        try:
            mission_channel, mission_forum, informes_forum = get_channels(interaction)
        except Exception as e:
            raise StopError(f"No se pudo obtener los canales necesarios: {e}") from e

        # Find and parse the original message
        try:
            original_message = await mission_channel.fetch_message(message_id)
            if not (original_message.author == self.client.user and original_message.content.startswith("# __T")):
                raise StopError("El mensaje especificado no es un anuncio de misión válido.")
        except nextcord.NotFound as e:
            raise StopError("No se pudo encontrar el mensaje especificado.") from e

        parsed_notice = parse_notice(original_message.content)
        # Override values with provided inputs (keep existing if None)
        parsed_notice["turn"] = turn or parsed_notice["turn"]
        parsed_notice["mission_name"] = mission_name or parsed_notice["mission_name"]
        parsed_notice["players"] = players or parsed_notice["players"]
        parsed_notice["tier"] = tier or parsed_notice["tier"]
        parsed_notice["disponibility"] = disponibility or parsed_notice["disponibility"]
        parsed_notice["tags"] = [tag.strip() for tag in tags.split(",")] if tags else parsed_notice["tags"]
        parsed_notice["duration"] = duration or parsed_notice["duration"]

        # Validate that no required values are None or empty
        for key, val in parsed_notice.items():
            if not val and key not in ["participants", "tags"]:
                raise StopError(f"Campo requerido '{key}' está vacío o no se pudo extraer del anuncio original.")

        await interaction.followup.send(
            f"Editando anuncio de misión: {parsed_notice['mission_name']}...\n"
            f"Por favor, responde al mensaje con la nueva descripción de la misión dentro de los siguientes 2 minutos. "
            f"Si no quieres cambiar la descripción, responde con 'sin cambios'."
        )

        def check_response(interaction: nextcord.Interaction) -> None:
            async def wait_for_response() -> None:
                og_msg = await interaction.original_message()
                try:
                    response: Message = await self.client.wait_for(
                        "message",
                        timeout=120,
                        check=lambda m: (
                            m.channel == interaction.channel
                            and m.author == interaction.user
                            and m.reference is not None
                            and m.reference.message_id == og_msg.id
                        ),
                    )
                    new_description = response.content.strip()
                    if new_description.lower() != "sin cambios":
                        parsed_notice["description"] = new_description

                    # Generate new announcement content
                    new_announcement = mission_announcement(
                        parsed_notice["description"],
                        ", ".join(parsed_notice["tags"]),
                        parsed_notice["mission_name"],
                        narrator,
                        parsed_notice["players"],
                        parsed_notice["duration"],
                        parsed_notice["disponibility"],
                    )

                    # Preserve participants section from original message
                    if parsed_notice["participants"]:
                        new_announcement += "\n**Participantes:**"
                    for participant in parsed_notice["participants"]:
                        new_announcement += (
                            f"\n- {participant['emoji']} {participant['mention']}: {participant['roles']}"
                        )
                    coord_thread_id = parsed_notice["coord_thread"]
                    report_thread_id = parsed_notice["report_thread"]
                    coord_thread = mission_channel.guild.get_thread(int(coord_thread_id))
                    report_thread = mission_channel.guild.get_thread(int(report_thread_id))
                    if not coord_thread or not report_thread:
                        raise StopError("No se pudieron encontrar los hilos de coordinación o informe.")
                    # Preserve thread links
                    new_announcement += f"Coordinación: {coord_thread.mention}"
                    new_announcement += f"\nInforme: {report_thread.mention}"

                    # Update the original message
                    await original_message.edit(content=new_announcement)

                    # Update corresponding threads
                    if first_message := await get_thread_initial_message(coord_thread):
                        await first_message.edit(content=new_announcement)

                        if first_message := await get_thread_initial_message(report_thread):
                            await first_message.edit(content=new_announcement)

                    await response.reply(f"Anuncio de misión editado exitosamente: {parsed_notice['mission_name']}")

                except TimeoutError:
                    await og_msg.reply("No se recibió respuesta dentro del período de espera.")
                except StopError as e:
                    await og_msg.reply(f"Error: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error in edit_notice: {e}")
                    await og_msg.reply(f"Error inesperado: {e}")

            asyncio.create_task(wait_for_response())  # noqa: RUF006

        check_response(interaction)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent) -> None:
        """Handle reaction added to mission announcement messages."""
        guild, user, channel = await self._process_reaction(payload)
        if not guild or not user or not channel:
            return

        async def process_add() -> None:
            message = await channel.fetch_message(payload.message_id)
            logger.info(f"Reaction added by {user.name} ({user.id}) to message {message.id}")
            emoji = f"{payload.emoji}" or "❓"
            if message.author == self.client.user and message.content.startswith("# __T"):
                content = message.content
                if user.mention in content:
                    return  # User already mentioned, no need to add again

                content = add_participant(content, user, emoji)
                await message.edit(content=content)
                # Extract thread mention from the content and add user to it
                if thread := extract_thread(guild, content):
                    await thread.add_user(user)
                    if first_message := await get_thread_initial_message(thread):
                        add_participant(first_message.content, user, emoji)
                        await first_message.edit(content=add_participant(first_message.content, user, emoji))

                # Add user to report thread if it exists
                name = extract_mission_name(content)
                if name and (report_thread := find_report_thread(name, guild)):
                    await report_thread.add_user(user)
                    if first_message := await get_thread_initial_message(report_thread):
                        await first_message.edit(content=add_participant(first_message.content, user, emoji))

        await self._process_message_safely(payload.message_id, process_add)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent) -> None:
        """Handle reaction removed from mission announcement messages."""
        guild, user, channel = await self._process_reaction(payload)
        if not guild or not user or not channel:
            return

        async def process_remove() -> None:
            message = await channel.fetch_message(payload.message_id)
            logger.info(f"Reaction removed by {user.name} ({user.id}) from message {message.id}")

            if message.author == self.client.user and message.content.startswith("# __T"):
                content = message.content
                if user.mention in content:
                    content = remove_participant(content, user)
                    await message.edit(content=content)

                    if thread := extract_thread(guild, content):
                        await thread.remove_user(user)
                        if first_message := await get_thread_initial_message(thread):
                            await first_message.edit(content=remove_participant(first_message.content, user))

                    name = extract_mission_name(content)
                    if name and (report_thread := find_report_thread(name, guild)):
                        await report_thread.remove_user(user)
                        if first_message := await get_thread_initial_message(report_thread):
                            await first_message.edit(content=remove_participant(first_message.content, user))

        await self._process_message_safely(payload.message_id, process_remove)


async def create_threads(
    interaction: Interaction,
    mission_name: str,
    tier: str,
    narrator: Member,
    mission_forum: ForumChannel,
    informes_forum: ForumChannel,
    announcement: str,
) -> tuple[str, Thread]:
    """Create mission coordination and report threads in the specified forums."""
    # Create coordination forum thread
    gm_tag, tier_tag = get_tags(mission_forum, narrator, tier)
    if not gm_tag or not tier_tag:
        raise StopError(f"Could not find a valid forum {'GM' if not gm_tag else 'tier'} tag: narrator={narrator.name}, narrator_id={narrator.id}, id_type={type(narrator.id)}, tier={tier}")

    coord_thread = await post_forum_announcement(
        interaction, mission_name, announcement, tags=[gm_tag, tier_tag], forum=mission_forum
    )
    if coord_thread is None:
        raise StopError("Could not create the forum thread for the mission.")
    announcement += f"Coordinación: {coord_thread.mention}"

    # Create report forum thread
    gm_tag, tier_tag = get_tags(informes_forum, narrator, tier)
    if not gm_tag or not tier_tag:
        raise StopError(f"Could not find a valid forum {'GM' if not gm_tag else 'tier'} tag: narrator={narrator.name}, narrator_id={narrator.id}, id_type={type(narrator.id)}, tier={tier}")
    report_thread = await post_forum_announcement(
        interaction, mission_name, announcement, tags=[gm_tag, tier_tag], forum=informes_forum
    )
    if report_thread is None:
        raise StopError("Could not create the forum thread for the mission.")
    announcement += f"\nInforme: {report_thread.mention}\n\n**Participantes:**"
    return announcement, report_thread


async def get_thread_initial_message(thread: Thread) -> Message | None:
    """Get the initial message content of a thread."""
    message = await thread.fetch_message(thread.id)
    return message or None


def remove_participant(content: str, user: Member) -> str:
    """Remove a participant from the mission announcement content."""
    lines = content.split("\n")
    lines = [line for line in lines if user.mention not in line or line.strip().startswith("Narrador:")]
    return "\n".join(lines)


def add_participant(content: str, user: Member, emoji: str) -> str:
    """Add a participant to the mission announcement content."""
    if "**Participantes:**" not in content:
        content += "\n**Participantes:**"
    if user.mention not in content:
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


def parse_notice(text: str) -> dict[str, Any]:
    """Parse a mission announcement text into its components."""
    lines = text.split("\n")
    mission_info = {
        "mission_name": "",
        "tier": "",
        "turn": 0,
        "description": "",
        "narrator": "",
        "players": "",
        "duration": "",
        "disponibility": "",
        "tags": [],
        "participants": [],
    }

    # Extract mission name
    if lines and lines[0].startswith("# __") and lines[0].endswith("__"):
        mission_line = lines[0][4:-2].strip()
        # Extract turn, tier and mission name in one regex
        turn_tier_match = re.match(r"T(\d+) Lvl (Alto|Bajo): (.+)", mission_line)
        if turn_tier_match:
            mission_info["turn"] = int(turn_tier_match.group(1))
            mission_info["tier"] = turn_tier_match.group(2)
            mission_info["mission_name"] = turn_tier_match.group(3)
        else:
            mission_info["mission_name"] = mission_line

    # Extract description
    desc_lines = []
    for line in lines[1:]:
        if line.startswith("Narrador:"):
            break
        desc_lines.append(line)
    mission_info["description"] = "\n".join(desc_lines).strip()

    # Extract other fields
    for line in lines:
        if line.startswith("Narrador:"):
            mission_info["narrator"] = line[len("Narrador:"):].strip()
        elif line.startswith("Tamaño de party:"):
            mission_info["players"] = line[len("Tamaño de party:"):].strip()
        elif line.startswith("Duración:"):
            mission_info["duration"] = line[len("Duración:"):].strip()
        elif line.startswith("Disponibilidad:"):
            mission_info["disponibility"] = line[len("Disponibilidad:"):].strip()
        elif line.startswith("Tags:"):
            tags_str = line[len("Tags:"):].strip()
            mission_info["tags"] = [tag.strip() for tag in tags_str.split(",")] if tags_str else []

    # Extract participants
    participant_section = False
    for line in lines:
        if line.startswith("**Participantes:**"):
            participant_section = True
            continue
        if participant_section:
            if line.startswith("- "):
                match = re.match(r"- (.+?) \((<@!?\d+>)\): (.+)", line)
                if match:
                    emoji, mention, roles = match.groups()
                    mission_info["participants"].append({"emoji": emoji, "mention": mention, "roles": roles})
            else:
                break

    # Extract coordination and report thread links
    coord_thread = None
    report_thread = None
    for line in lines:
        if line.startswith("Coordinación:") and "<#" in line:
            match = re.search(r"<#(\d+)>", line)
            if match:
                coord_thread = match.group(1)
        elif line.startswith("Informe:") and "<#" in line:
            match = re.search(r"<#(\d+)>", line)
            if match:
                report_thread = match.group(1)

    if coord_thread is None:
        raise ValueError("Coordination thread ID not found in mission announcement")
    if report_thread is None:
        raise ValueError("Report thread ID not found in mission announcement")

    mission_info["coord_thread"] = coord_thread
    mission_info["report_thread"] = report_thread

    return mission_info
