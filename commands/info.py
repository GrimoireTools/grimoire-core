"""Discord bot commands for character information and status management."""

import math
from typing import Any, Self
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option, not_none
from nextcord import Interaction, Member, SlashOption
from commands.utils.caliban_utils import caliban_speaks
from controllers.lvl_groups_controller import LEVEL_GROUPS, LevelGroup, LvlGroupController
from controllers.pjs_controller import PJsController


class InfoCommands(Cog):
    """Commands related to character information and status."""

    @standard_command(description="Entrega la info de tu personaje")
    async def status(self: Self, interaction: Interaction, user: Member = default_user_option) -> Any:
        """Display the status of a character, including money and downtime."""
        user_id = not_none(interaction.user).id if user is None else user.id
        pj = PJsController().get_pj_row(user_id)
        coins = pj.to_coin_list()
        dt = not_none(pj.Downtime)

        message = f"""# Status de {pj.Name}
    - Jugador: {pj.Player}
    - Clase: {pj.Class} Lvl {pj.level()}{", " if pj.Archetypes else ""}{pj.Archetypes}
    - Ascendencia: {pj.Ancestry}, {pj.Heritage}
    - Dinero: {coins.pretty_print()}, **Total: {coins.total():.2f}gp**
    - Downtime: {dt // 7} semanas y {dt % 7} dias ({dt} dias)
    """
        await interaction.followup.send(message)
        await caliban_speaks(interaction)

    @standard_command("Calcula el costo de DT de hacer múltiples retrain a la vez")
    async def retrain_info(
        self: Self,
        interaction: Interaction,
        amount: int = SlashOption(
            "retrains", description="Cantidad de retrains simultaneaos", required=True, min_value=1
        ),
        discount: bool = SlashOption("discount", description="Aplicar descuento", required=False, default=False),
    ) -> Any:
        """Calculate the downtime cost for multiple retrains at once."""
        base_cost = 5 if discount else 7
        cost = base_cost + math.ceil(base_cost * (math.log(amount * 1.5 - 0.5)))
        return await interaction.followup.send(
            f"Hacer {amount} retrain{'s' if amount > 1 else ''} a la vez costará {cost} días de DT"
        )

    @standard_command("Cambia el nivel de todos los personajes de un grupo")
    async def update_group_level(
        self: Self,
        interaction: Interaction,
        group: LevelGroup = SlashOption("level_group", required=True, choices=LEVEL_GROUPS),
        level: int | None = None,
    ) -> Any:
        """Update the level of all characters in a specified group."""
        sh = LvlGroupController()
        old_level = sh.get_level_row(group).Level
        if level is None:
            return await interaction.followup.send(
                f"Nivel actual del grupo {group}: {old_level}. Usa el comando con un nivel para actualizarlo."
            )
        if level < 1 or level > 20:
            return await interaction.followup.send("El nivel debe estar entre 1 y 20.")
        if level == old_level:
            return await interaction.followup.send(f"El nivel del grupo {group} ya es {level}.")
        sh.set_level(group, level)
        return await interaction.followup.send(f"Nivel del grupo {group} actualizado: {old_level} -> {level}")
