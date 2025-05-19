from typing import Any, Self
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option, not_none
from nextcord import Interaction, Member, SlashOption

from controllers.pjs_controller import PJsController
from controllers.salary_controller import SalaryController


class SalaryCommands(Cog):

    @standard_command("Gana el downtime y dinero esperado de terminar una misión")
    async def dgm_salary(
        self: Self,
        interaction: Interaction,
        turno: int = SlashOption("turno", description="Turno en el que se completó la misión", required=True),
        target: Member = default_user_option,
    ) -> Any:
        user_id = not_none(interaction.user).id if target is None else target.id
        sh_pjs = PJsController()
        pj = sh_pjs.get_pj_row(user_id)
        sh_salary = SalaryController()

        sueldo_gp, sueldo_dt = sh_salary.get_salary(turno), sh_salary.get_downtime()
        new_money = not_none(pj.Money_total) + sueldo_gp
        pj.update_money(new_money)

        pj.Downtime = not_none(pj.Downtime) + sueldo_dt
        pj.Last_turn = f"T{turno}"
        sh_pjs.set_row(pj)

        return await interaction.followup.send(
            (
                f"{pj.Name}: Misión turno {turno} completada!"
                f"\n Se te suma el sueldo de la misión:"
                f" {sueldo_gp: .2f}gp (ahora tienes {new_money: .2f}gp)"
                f"\n Se te suman {sueldo_dt} días de dt "
                f"(ahora tienes {pj.Downtime} dias de dt)"
            )
        )
