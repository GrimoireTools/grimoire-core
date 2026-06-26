from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController
from commands.utils.wod_utils import dots
from system_data import Attribute, ATTRIBUTES

ATTRIBUTE_CHOICES = ATTRIBUTES


class AttributesCommands(Cog):

    @slash_command(name="attribute", guild_ids=[CRI_GUILD_ID], description="Manage character attributes")
    async def attribute_group(self, interaction: Interaction):
        pass

    # ── /attribute set ────────────────────────────────────────────────────────
    @attribute_group.subcommand(name="set", description="Sets a single attribute to a value (1–5) (max 8 for vampires)")
    @try_command
    async def attribute_set(
        self: Self,
        interaction: Interaction,
        attribute: Attribute = SlashOption(
            "attribute", "Attribute to set", required=True, choices=ATTRIBUTE_CHOICES),
        value: int = SlashOption(
            "value", "New value (1–5)", required=True, min_value=1, max_value=5),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        max_value = pj.max_attr()
        if value > max_value:
            return await interaction.followup.send(
                f"Error: The value for {attribute} exceeds the maximum of {max_value} for your character type ({pj.Char_type})."
            )
        old = pj.attribute(attribute)
        pj.attribute(attribute, value)
        sh.set_row(pj)
        await interaction.followup.send(f"**{pj.Name}** — {attribute}: {dots(old, max_value)} → {dots(value, max_value)} ({old} → {value})")

    # ── /attribute view ───────────────────────────────────────────────────────
    @attribute_group.subcommand(name="view", description="Shows the current value of a single attribute")
    @try_command
    async def attribute_view(
        self: Self,
        interaction: Interaction,
        attribute: Attribute = SlashOption(
            "attribute", "Attribute to view", required=True, choices=ATTRIBUTE_CHOICES),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController.cached().get_pj_row(user_id)
        value = pj.attribute(attribute)
        max_value = pj.max_attr()
        await interaction.followup.send(f"**{pj.Name}** — {f"{attribute} ({value}):".rjust(20)} {dots(value, max_value)}")

    # ── /attributes set_all ───────────────────────────────────────────────────
    @slash_command(name="attributes", guild_ids=[CRI_GUILD_ID], description="Set all 9 attributes at once")
    @try_command
    async def attributes_set_all(
        self: Self,
        interaction: Interaction,
        strength: int = SlashOption(
            "strength", required=True, min_value=1, max_value=8),
        dexterity: int = SlashOption(
            "dexterity", required=True, min_value=1, max_value=8),
        stamina: int = SlashOption(
            "stamina", required=True, min_value=1, max_value=8),
        charisma: int = SlashOption(
            "charisma", required=True, min_value=1, max_value=8),
        manipulation: int = SlashOption(
            "manipulation", required=True, min_value=1, max_value=8),
        appearance: int = SlashOption(
            "appearance", required=True, min_value=1, max_value=8),
        perception: int = SlashOption(
            "perception", required=True, min_value=1, max_value=8),
        intelligence: int = SlashOption(
            "intelligence", required=True, min_value=1, max_value=8),
        wits: int = SlashOption("wits", required=True,
                                min_value=1, max_value=8),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        max_value = pj.max_attr()
        if any(attr > max_value for attr in [strength, dexterity, stamina, charisma, manipulation, appearance, perception, intelligence, wits]):
            return await interaction.followup.send(
                f"Error: One or more attributes exceed the maximum value of {max_value} for your character type ({pj.Char_type})."
            )

        pj.set_attributes({
            "Strength": strength,
            "Dexterity": dexterity,
            "Stamina": stamina,
            "Charisma": charisma,
            "Manipulation": manipulation,
            "Appearance": appearance,
            "Perception": perception,
            "Intelligence": intelligence,
            "Wits": wits,
        })
        sh.set_row(pj)
        lines = "\n".join(
            f"  {k:<14} {dots(v, max_value)} ({v})"
            for k, v in pj.Attributes.items()
        )
        await interaction.followup.send(f"**{pj.Name}** — Attributes updated:\n```\n{lines}\n```")
