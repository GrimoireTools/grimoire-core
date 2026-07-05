from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption, Member

from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command, default_user_option
from controllers.pjs_controller import PJsController
from controllers.cemetery_controller import CemeteryRow, CemeteryController


class KillCommands(Cog):
    @slash_command(name="kill", guild_ids=[CRI_GUILD_ID], description="Move a character to the cemetery")
    @try_command
    async def kill(
        self: Self,
        interaction: Interaction,
        turn: int = SlashOption("turn", "Turn on which the character died", required=True),
        cause: str = SlashOption("cause", "Cause of death", required=True),
        user: Member = default_user_option,
    ) -> Any:
        user_id = not_none(interaction.user).id if user is None else user.id

        pj_sh = PJsController()
        pj = pj_sh.get_pj_row(user_id)

        dead = CemeteryRow(
            Name=pj.Name,
            Discord_id=pj.Discord_id,
            Player=pj.Player,
            Turn_of_death=turn,
            Cause_of_death=cause,
            Char_type=pj.Char_type,
            Attributes=pj.Attributes,
            Abilities=pj.Abilities,
            Specialties=pj.Specialties,
            Resources=pj.Resources,
        )

        cem_sh = CemeteryController()
        cem_sh.insert_row(dead, cem_sh.find_first_empty_row("A", strict=True))

        pj_sh.delete_row(pj)

        await interaction.followup.send(
            f"**{pj.Name}** ({pj.Char_type}) has been moved to the cemetery.\nDied on turn **{turn}**. Cause: {cause}"
        )
