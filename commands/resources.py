from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from commands.utils.quotes import quotify
from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController


class ResourcesCommands(Cog):

    @slash_command(name="resource", guild_ids=[CRI_GUILD_ID], description="Manage character resources")
    async def resource_group(self, interaction: Interaction):
        pass

    @resource_group.subcommand(name="set", description="Creates or overwrites a named resource")
    @try_command
    async def resource_set(
        self: Self,
        interaction: Interaction,
        name: str = SlashOption("name", "Resource name", required=True),
        value: int = SlashOption("value", "New value", required=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        pj.resource(name, value)
        sh.set_row(pj)
        await interaction.followup.send(quotify(f"**{pj.Name}** — {name} set to **{value}**."))

    @resource_group.subcommand(name="add", description="Adds to or subtracts from a resource (negative to subtract)")
    @try_command
    async def resource_add(
        self: Self,
        interaction: Interaction,
        name: str = SlashOption("name", "Resource name",
                                required=True, autocomplete=True),
        amount: int = SlashOption(
            "amount", "Amount to add (negative to subtract)", required=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        before = pj.resource(name)
        after = pj.resource(name, before + amount)
        sh.set_row(pj)
        direction = "gains" if amount >= 0 else "loses"
        await interaction.followup.send(quotify(
            f"**{pj.Name}** {direction} **{abs(amount)}** {name}.\n{before} -> {after}"
        ))

    @resource_group.subcommand(name="remove", description="Removes a resource from the character sheet")
    @try_command
    async def resource_remove(
        self: Self,
        interaction: Interaction,
        name: str = SlashOption(
            "name", "Resource to remove", required=True, autocomplete=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        if name not in pj.Resources:
            return await interaction.followup.send(f"Resource **{name}** not found.")
        del pj.Resources[name]
        sh.set_row(pj)
        await interaction.followup.send(quotify(f"**{pj.Name}** — **{name}** removed."))

    @resource_group.subcommand(name="list", description="Shows all resources for your character")
    @try_command
    async def resource_list(
        self: Self,
        interaction: Interaction,
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController.cached().get_pj_row(user_id)
        if not pj.Resources:
            return await interaction.followup.send(quotify(f"**{pj.Name}** has no resources."))
        lines = "\n".join(f"  {k}: {v}" for k,
                          v in sorted(pj.Resources.items()))
        await interaction.followup.send(quotify(f"**{pj.Name}** — Resources:\n```\n{lines}\n```"))

    # ── Autocomplete ──────────────────────────────────────────────────────────

    @resource_add.on_autocomplete("name")
    async def _autocomplete_add(self, interaction: Interaction, name: str):
        await self._resource_autocomplete(interaction, name)

    @resource_remove.on_autocomplete("name")
    async def _autocomplete_remove(self, interaction: Interaction, name: str):
        await self._resource_autocomplete(interaction, name)

    async def _resource_autocomplete(self, interaction: Interaction, query: str):
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            names = list(pj.Resources.keys())
        except Exception:
            names = []
        if query:
            names = [n for n in names if n.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])
