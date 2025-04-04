from typing import Any, Self
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option, not_none
from nextcord import Interaction, Member, SlashOption

from controllers.pjs_controller import PJsController
from controllers.salary_controller import SalaryController

AFK_GOLD = [
    34 / 2,
    58 / 2,
    95 / 2,
    163 / 2,
    258 / 2,
    375 / 2,
    545 / 2,
    750 / 2,
    1075 / 2,
    1500 / 2,
    2175 / 2,
    3125 / 2,
    4750 / 2,
    6875 / 2,
    10375 / 2,
    15625 / 2,
    24500 / 2,
    40000 / 2,
    68750 / 2,
    87500 / 2,
]


class SalaryCommands(Cog):

    @standard_command("Gana el downtime y dinero esperado de terminar una misión")
    async def salary(
        self: Self,
        interaction: Interaction,
        level: int,
        turno: int = SlashOption("turno", description="Turno en el que se completó la misión", required=True),
        target: Member = default_user_option,
    ) -> Any:
        user_id = not_none(interaction.user).id if target is None else target.id
        sh_pjs = PJsController()
        pj = sh_pjs.get_pj_row(user_id)
        sh_salary = SalaryController()

        sueldo_gp, sueldo_dt = sh_salary.get_salary(level), sh_salary.get_downtime()
        new_money = not_none(pj.Money_total) + sueldo_gp
        pj.update_money(new_money)

        pj.Downtime = not_none(pj.Downtime) + sueldo_dt
        pj.Last_turn = f"T{turno}"
        sh_pjs.set_row(pj)

        return await interaction.followup.send(
            (
                f"{pj.Name}: Misión nivel {level} completada!"
                f"\n Se te suma el sueldo de la misión:"
                f" {sueldo_gp: .2f}gp (ahora tienes {new_money: .2f}gp)"
                f"\n Se te suman {sueldo_dt} días de dt "
                f"(ahora tienes {pj.Downtime} dias de dt)"
            )
        )

    @standard_command("Gana el downtime y dinero obtenido en un turno en que no jugaste.")
    async def afk_salary(
        self: Self,
        interaction: Interaction,
        level: int = SlashOption(
            "level", description="nivel del turno en que no jugaste.", required=True, max_value=20, min_value=1
        ),
        target: Member = default_user_option,
    ) -> Any:
        user_id = not_none(interaction.user).id if target is None else target.id
        sh_pjs = PJsController()
        pj = sh_pjs.get_pj_row(user_id)
        sueldo_gp, sueldo_dt = AFK_GOLD[level - 1], 28

        new_money = not_none(pj.Money_total) + sueldo_gp
        pj.update_money(new_money)

        pj.Downtime = not_none(pj.Downtime) + sueldo_dt
        sh_pjs.set_row(pj)

        return await interaction.followup.send(
            (
                f"{pj.Name}: Turno nivel {level} no jugado!"
                f"\n Se te suma el sueldo de existir:"
                f" {sueldo_gp: .2f}gp (ahora tienes {new_money: .2f}gp)"
                f"\n Se te suman {sueldo_dt} días de dt "
                f"(ahora tienes {pj.Downtime} dias de dt)"
            )
        )
