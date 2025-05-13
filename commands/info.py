import math
from typing import Any, Self
import caliban
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option, not_none
from nextcord import Interaction, Member, SlashOption
from commands.utils.caliban_utils import *
from controllers.pjs_controller import PJsController
from controllers.salary_controller import get_level_global, update_level_global


class InfoCommands(Cog):
    @standard_command(description="Entrega la info de tu personaje")
    async def status(self: Self, interaction: Interaction, user: Member = default_user_option) -> Any:
        user_id = not_none(interaction.user).id if user is None else user.id
        pj = PJsController().get_pj_row(user_id)
        coins = pj.to_coin_list()
        dt = not_none(pj.Downtime)

        caliban_message = ""
        if pj.Caliban_met == 1:
            caliban_message = caliban.get_message_sometimes(40)

        message = f"""# Status de {pj.Name}
    - Jugador: {pj.Player}
    - Clase: {pj.Class}{", " if pj.Archetypes else ""}{pj.Archetypes}
    - Ascendencia: {pj.Ancestry}, {pj.Heritage}
    - Dinero: {coins.pretty_print()}, **Total: {coins.total():.2f}gp**
    - Downtime: {dt // 7} semanas y {dt % 7} dias ({dt} dias)
    """
        await interaction.followup.send(message)
        await send_caliban_message(interaction, caliban_message)

    @standard_command("Calcula el costo de DT de hacer múltiples retrain a la vez")
    async def retrain_info(
        self: Self,
        interaction: Interaction,
        amount: int = SlashOption(
            "retrains", description="Cantidad de retrains simultaneaos", required=True, min_value=1
        ),
    ) -> Any:
        cost = 7 + math.ceil(7 * (math.log(amount * 1.5 - 0.5)))
        return await interaction.followup.send(
            f"Hacer {amount} retrain{'s' if amount > 1 else ''} a la vez costará {cost} días de DT"
        )

    @standard_command("Cambia el nivel de todos los personajes")
    async def update_global_level(self: Self, interaction: Interaction, level: int | None = None) -> Any:
        old_level = get_level_global()
        update_level_global(level)
        return await interaction.followup.send(f"Nivel global actualizado: {old_level} -> {level}")
