from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJRow, PJsController
from system_data import ATTRIBUTES, CHARACTER_TYPES, DEFAULT_RESOURCES, CharType


class RegisterCommands(Cog):
    @slash_command(name="register", guild_ids=[CRI_GUILD_ID], description="Register a new character")
    @try_command
    async def register(
        self: Self,
        interaction: Interaction,
        name: str = SlashOption("name", "Character name", required=True),
        player: str = SlashOption("player", "Player name", required=True),
        char_type: CharType = SlashOption(
            "type",
            "Character type",
            required=True,
            choices=CHARACTER_TYPES,
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()

        if sh.character_exists(user_id):
            existing = sh.get_pj_row(user_id)
            return await interaction.followup.send(
                f"You already have a registered character: **{existing.Name}** ({existing.Char_type}).\n"
                f"Contact a GM if you need to replace it."
            )

        pj = PJRow(
            Name=name,
            Discord_id=str(user_id),
            Player=player,
            Last_turn=0,
            Char_type=char_type,
            Attributes=dict.fromkeys(ATTRIBUTES, 0),
            Abilities={},
            Specialties={},
            Resources=DEFAULT_RESOURCES[char_type].copy(),
        )

        sh.insert_row(pj, sh.find_first_empty_row("A", strict=True))

        resources_str = ", ".join(f"{k}: {v}" for k, v in DEFAULT_RESOURCES[char_type].items())
        await interaction.followup.send(
            f"**{name}** registered as a **{char_type}**!\n"
            f"Starting resources: {resources_str}\n"
            f"Use `/attributes` to set your attributes and `/ability set` to add your abilities."
        )
