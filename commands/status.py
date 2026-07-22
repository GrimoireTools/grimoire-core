from typing import Any, Self

from nextcord import slash_command, Member, Interaction

from commands.utils.quotes import quotify
from controllers.lib.cog import Cog
from controllers.lib.utils import default_user_option, CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController

class StatusCommands(Cog):
    """Commands related to character info."""

    @slash_command(name="status", guild_ids=[CRI_GUILD_ID], description="Display status of a character")
    @try_command
    async def status(
        self: Self,
        interaction: Interaction,
        user: Member = default_user_option
    ) -> Any:
        user_id = not_none(interaction.user).id if user is None else user.id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)

        subtype_str = ", ".join(f"{k}: {v}" for k, v in pj.SubChar_type.items())
        message = f"""# Status de {pj.Name}
    - Jugador: {pj.Player}
    - Tipo: {pj.Char_type}
    - {subtype_str}
    - XP: {pj.Resources["XP"]}
    - Willpower: {pj.Resources["Willpower"]}
    """
        await interaction.followup.send(quotify(message,interaction))
