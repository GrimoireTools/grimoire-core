from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController
from commands.utils.wod_utils import dots
from system_data import PREDEFINED_ABILITIES


class AbilitiesCommands(Cog):

    @slash_command(name="ability", guild_ids=[CRI_GUILD_ID], description="Manage character abilities")
    async def ability_group(self, interaction: Interaction):
        pass

    # ── /ability set ────────────────────────────────────────────────────────────
    @ability_group.subcommand(name="set", description="Sets an ability value (0–8); type any name to add a custom ability")
    @try_command
    async def ability_set(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption(
            "ability", "Ability name (predefined or custom)", required=True, autocomplete=True),
        value: int = SlashOption(
            "value", "New value (0–8)", required=True, min_value=0, max_value=5),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        old = pj.ability(ability)
        pj.ability(ability, value)
        sh.set_row(pj)
        await interaction.followup.send(f"**{pj.Name}** — {ability}: {dots(old)} → {dots(value)}")

    # ── /ability view ───────────────────────────────────────────────────────────
    @ability_group.subcommand(name="view", description="Shows an ability value and specialty if any")
    @try_command
    async def ability_view(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption(
            "ability", "Ability name", required=True, autocomplete=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController.cached().get_pj_row(user_id)
        value = pj.ability(ability)
        spec = pj.specialty(ability)
        spec_str = f"  *(specialty: {spec})*" if spec else ""
        await interaction.followup.send(f"**{pj.Name}** — {ability}: {dots(value)}{spec_str}")

    # ── /specialty set ────────────────────────────────────────────────────────
    @slash_command(name="specialty", guild_ids=[CRI_GUILD_ID], description="Manage ability specialties")
    async def specialty_group(self, interaction: Interaction):
        pass

    @specialty_group.subcommand(name="set", description="Adds or replaces a specialty for an ability")
    @try_command
    async def specialty_set(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption(
            "ability", "Ability to specialise in", required=True, autocomplete=True),
        description: str = SlashOption(
            "description", "Specialty description (e.g. 'Haymaker')", required=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        pj.specialty(ability, description)
        sh.set_row(pj)
        await interaction.followup.send(
            f"**{pj.Name}** — {ability} specialty set to **{description}**. "
            f"10s will count as 2 successes when rolling this ability."
        )

    @specialty_group.subcommand(name="remove", description="Removes the specialty from an ability")
    @try_command
    async def specialty_remove(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption(
            "ability", "Ability to remove specialty from", required=True, autocomplete=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        if ability not in pj.Specialties:
            return await interaction.followup.send(f"**{ability}** has no specialty.")
        del pj.Specialties[ability]
        sh.set_row(pj)
        await interaction.followup.send(f"**{pj.Name}** — specialty for **{ability}** removed.")

    # ── Autocomplete ──────────────────────────────────────────────────────────

    @ability_set.on_autocomplete("ability")
    async def _ac_ability_set(self, interaction: Interaction, query: str):
        await self._ability_autocomplete(interaction, query, include_custom=True)

    @ability_view.on_autocomplete("ability")
    async def _ac_ability_view(self, interaction: Interaction, query: str):
        await self._ability_autocomplete(interaction, query, include_custom=True)

    @specialty_set.on_autocomplete("ability")
    async def _ac_specialty_set(self, interaction: Interaction, query: str):
        # Only abilities the character actually has a value in
        await self._ability_autocomplete(interaction, query, only_known=True)

    @specialty_remove.on_autocomplete("ability")
    async def _ac_specialty_remove(self, interaction: Interaction, query: str):
        # Only abilities that already have a specialty
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            names = list(pj.Specialties.keys())
        except Exception:
            names = []
        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])

    async def _ability_autocomplete(
        self,
        interaction: Interaction,
        query: str,
        include_custom: bool = False,
        only_known: bool = False,
    ):
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            known = list(pj.Abilities.keys())
        except Exception:
            known = []
            pj = None

        if only_known:
            names = known
        elif include_custom:
            # Predefined first, then any custom skills the character already has
            custom = [s for s in known if s not in PREDEFINED_ABILITIES]
            names = PREDEFINED_ABILITIES + custom
        else:
            names = PREDEFINED_ABILITIES

        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])
