from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJRow, PJsController
from system_data import ATTRIBUTES, CHARACTER_TYPES, DEFAULT_RESOURCES, CharType, SUB_CHARACTER_TYPES, SUBTYPE_VALUE_SOURCE


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
            SubChar_type=SUB_CHARACTER_TYPES[char_type].copy(),
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
            f"Use `/attributes_set_all` to set your attributes"
            f"Use `/ability_set_talents` to add your talents."
            f"Use `/ability_set_skills` to add your skills."
            f"Use `/ability_set_knowledges` to add your knowledges."
        )

    @slash_command(name="set_subtype", guild_ids=[CRI_GUILD_ID], description="Set the subtype of your character")
    @try_command
    async def set_subtype(
        self: Self,
        interaction: Interaction,
        subtype: str = SlashOption("subtype", "Character subtype", required=True, autocomplete=True),
        value: str = SlashOption("value", "Value for the subtype", required=True, autocomplete=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        pj.subtype(subtype, value)
        sh.set_row(pj)
        await interaction.followup.send(f"**{pj.Name}**'s **{subtype}** has been set to **{value}**.")

    # ── Autocomplete ──────────────────────────────────────────────────────────

    @set_subtype.on_autocomplete("subtype")
    async def _autocomplete_set(self, interaction: Interaction, query: str) -> None:
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            subtypes = list(pj.SubChar_type.keys())
        except Exception:
            subtypes = []
        if query:
            subtypes = [s for s in subtypes if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(subtypes)

    @set_subtype.on_autocomplete("value")
    async def _autocomplete_value(self, interaction: Interaction, query: str) -> None:
        values: list[str] = []

        choices = interaction.data.get("options") if interaction.data else None
        if choices:
            subtype_opt = next(
                (opt for opt in choices if opt.get("name") == "subtype"), None
            )
            raw_subtype = subtype_opt.get("value") if subtype_opt else None
            if isinstance(raw_subtype, str):
                values = SUBTYPE_VALUE_SOURCE.get(raw_subtype, [])

        if query:
            values = [v for v in values if v.lower().startswith(query.lower())]

        await interaction.response.send_autocomplete(values[:25])
