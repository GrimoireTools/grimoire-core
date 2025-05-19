from typing import Any, Self

from nextcord import SlashOption, Interaction

from controllers.lib.utils import not_none, parse_float_arg
from controllers.lib.cog import Cog, standard_command

from controllers.pjs_controller import PJsController, get_cache_name
from controllers.dt_log_controller import DtLogController


class DowntimeCommands(Cog):

    @standard_command("Cambia el Downtime de tu personaje")
    async def dt(self: Self, interaction: Interaction, amount: str) -> Any:
        amt = parse_float_arg(amount)
        sh = PJsController()
        user_id: int = not_none(interaction.user).id
        pj = sh.get_pj_row(user_id)
        pj_dt = not_none(pj.Downtime)

        if pj_dt + amt < 0:
            return await interaction.followup.send("No tienes suficiente downtime para esta transacción")

        new_total = pj_dt + amt
        pj.Downtime = new_total

        sh.set_row(pj)

        return await interaction.followup.send(
            (
                f"{pj.Name} {'gana' if amt > 0 else 'gasta'} {abs(amt)} semanas de downtime."
                f" Ahora tiene {new_total // 7} semanas y {new_total % 7} dias ({new_total} total)"
            )
        )

    @standard_command("Escribe una entrada en el log de DT")
    async def dt_log(self: Self, interaction: Interaction, turn: int, text: str) -> Any:
        user_id: int = not_none(interaction.user).id
        name = get_cache_name(user_id)
        DtLogController().set_log(user_id, turn, text)

        return await interaction.followup.send(f"Log de DT añadido a {name} en el turno {turn}:\n{text}")

    @standard_command("Muestra el log de DT")
    async def dt_log_check(
        self: Self,
        interaction: Interaction,
        turn: int = SlashOption("turno", "Turno desde donde checkear el log (havia atrás)", default=999),
        amount: int = SlashOption("cantidad-logs", "Cantidad de logs a mostrar", default=5),
    ) -> Any:
        user_id: int = not_none(interaction.user).id
        logs = DtLogController().get_user_logs(user_id)

        if len(logs) == 0:
            return await interaction.followup.send(f"{get_cache_name(user_id)} no tiene logs de DT")
        show_logs: list[str] = []
        for log in logs:
            if log.Turn <= turn:
                show_logs.append(log.pretty())
                if len(show_logs) >= amount:
                    break
        if len(show_logs) == 0:
            return await interaction.followup.send(
                f"No hay logs de DT para {get_cache_name(user_id)} en (o antes) del turno {turn}"
            )

        log_str = "\n".join(show_logs)
        return await interaction.followup.send(f"## Logs de DT de {logs[0].Name}:\n{log_str}")
