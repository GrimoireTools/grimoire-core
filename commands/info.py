from typing import Any, Self
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option, not_none
from nextcord import Interaction, Member, SlashOption

from controllers.pjs_controller import PJsController


class InfoCommands(Cog):
    @standard_command(description="Entrega la info de tu personaje")
    async def info(
        self: Self, interaction: Interaction, user: Member = default_user_option, full_data: bool = False
    ) -> Any:
        user_id = not_none(interaction.user).id if user is None else user.id
        pj = PJsController().get_pj_row(user_id)
        coins = pj.to_coin_list()
        dt = not_none(pj.Downtime)

        message = f"""# Status de {pj.Name}{"," if pj.Title else ""} {pj.Title}
- Jugador: {pj.Player}
- Clases: {pj.pretty_classes()}
- Raza: {pj.Race}, {pj.Subrace}
- Deidad: {pj.God}, {pj.Devotion} de Devoción
- Renombre: {pj.Renown}
- Dinero: {pj.to_coin_list().pretty_print()}, **Total: {pj.Money_total:.2f}gp**
- Downtime: {pj.Downtime // 1} semanas y {round(pj.Downtime % 1 * 10)} dias
Jugó por ultima vez en el turno {pj.Last_turn}
"""

        if full_data:
            message += f"""
- Favor divino: {pj.Divine_favor}
- Reputación: {pj.Reputation}
- Crianza: {pj.Crianza}
- Expresión: {pj.Expression}
- Infamia: {pj.Infamy}
- Mecenas: {pj.Mecenas}
    """
        await interaction.followup.send(message)
