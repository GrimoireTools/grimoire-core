from typing import Any, Self

from nextcord import SlashOption, Interaction

from controllers.lib.utils import not_none
from controllers.lib.cog import Cog, standard_command

from controllers.pjs_controller import RESOURCES, PJsController, Resource, get_cache_name
from controllers.dt_log_controller import DtLogController


class ResourcesCommands(Cog):

    @standard_command("Le suma o resta a un recurso de tu personaje")
    async def dgm_resource(
        self: Self,
        interaction: Interaction,
        resource: Resource = SlashOption("recurso", "Recurso a editar", choices=RESOURCES),
        amount: int = SlashOption("cantidad", "Cantidad a sumar o restar", default=0),
    ) -> Any:
        sh = PJsController()
        user_id: int = not_none(interaction.user).id
        pj = sh.get_pj_row(user_id)
        res_initial = pj.resource(resource)
        res_final = pj.resource(resource, amount)

        sh.set_row(pj)

        return await interaction.followup.send(
            (
                f"{pj.Name} {'gana' if amount > 0 else 'pierde'} {abs(amount)} {resource}.\n"
                f"{res_initial} -> {res_final}\n"
            )
        )
