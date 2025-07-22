"""Downtime management commands for Discord bot.

This module provides commands for managing character downtime in a role-playing
game context. Players can add or subtract downtime days from their characters
with validation to prevent negative balances.

Classes:
    DowntimeCommands: Cog containing downtime-related slash commands.

"""

from typing import Any, Self

import nextcord

from controllers.lib.utils import not_none
from controllers.lib.cog import Cog, standard_command

from controllers.pjs_controller import PJsController


class DowntimeCommands(Cog):
    """Commands related to managing Downtime for characters."""

    @standard_command("Cambia el Downtime de tu personaje")
    async def dt(self: Self, interaction: nextcord.Interaction, amount: int) -> Any:
        """Modify a character's downtime by the specified amount.

        Validates that the character has sufficient downtime before allowing
        negative transactions. Updates the character's downtime and provides
        feedback showing the change and new total in both days and weeks.

        Args:
            interaction (nextcord.Interaction): The Discord interaction object.
            amount (int): Days to add (positive) or subtract (negative) from downtime.

        Returns:
            Any: Response message indicating the downtime change and new total.
        """
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
            f"{pj.Name} {'gana' if amount > 0 else 'gasta'} {abs(amount)} dia{'s' if amount > 1 else ''} de downtime."
            f" Ahora tiene {new_total // 7} semanas y {new_total % 7} dias ({new_total} dias)"
        )
