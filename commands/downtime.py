from typing import Any, Self
from loguru import logger

import nextcord

from controllers.lib.utils import not_none
from controllers.lib.cog import Cog, standard_command

from controllers.PJsController import PJRow, PJsController


class DowntimeCommands(Cog):

    @standard_command("Cambia el Downtime de tu personaje")
    async def dt(self: Self, interaction: nextcord.Interaction, amount: int) -> Any:
        sh = PJsController()
        user_id: int = not_none(interaction.user).id
        pj = sh.get_pj_row(user_id)
        pj_dt = not_none(pj.Downtime)

        if pj_dt + amount < 0:
            return await interaction.followup.send("No tienes suficiente downtime para esta transacción")

        new_total = pj_dt + amount
        pj.Downtime = new_total

        sh.set_row(pj)

        return await interaction.followup.send(
            (
                f"{pj.Name} {'gana' if amount > 0 else 'gasta'} {abs(amount)} dias de downtime."
                f" Ahora tiene {new_total // 7} semanas y {new_total % 7} dias ({new_total} dias)"
            )
        )
