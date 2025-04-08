from typing import Any, Self
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import not_none
from controllers.pjs_controller import PJsController
from controllers.victory_pts_controller import VictoryPointsController, VictoryPointsRow
from nextcord import Interaction, Member, SlashOption

all_missions = VictoryPointsController().get_all_rows()
ACTIVE_MISSION_NAMES = [r.Mission_name for r in all_missions if r.Active == 1]
INACTIVE_MISSION_NAMES = [r.Mission_name for r in all_missions if r.Active == 0]


class VictoryPointsCommands(Cog):
    # add_victory_points: pts, user
    # remove_victory_points: pts, user
    @standard_command("Muestra la lista de misiones de pts de victoria activas")
    async def list_missions(self: Self, interaction: Interaction) -> None:
        global ACTIVE_MISSION_NAMES
        global INACTIVE_MISSION_NAMES
        sh = VictoryPointsController()
        missions = sh.get_all_rows()
        ACTIVE_MISSION_NAMES = [r.Mission_name for r in all_missions if r.Active == 1]
        INACTIVE_MISSION_NAMES = [r.Mission_name for r in all_missions if r.Active == 0]
        if len(missions) == 0:
            return await interaction.followup.send("No hay misiones registradas.")

        message = "**Misiones de puntos de victoria:**"
        for r in [m for m in missions if m.Active == 1]:
            message += f"\n- {r.Mission_name} ({r.Points} pts)"
            if len(message) >= 1800:
                message += "\n\n .... El resto de misiones no caben en el mensaje"
                break
        return await interaction.followup.send(message)

    @standard_command("Muestra el detalle de una misión de pts de victoria.")
    async def mission_details(
        self: Self,
        interaction: Interaction,
        mission_name: str = SlashOption("nombre-mision", "Nombre de la misión", True),
    ) -> None:
        sh = VictoryPointsController()
        mission_row = sh.get_mission_row(mission_name)
        if mission_row is None:
            return await interaction.followup.send(f"No se ha encontrado la misión *{mission_name}*.")
        message = f"**Misión:** {mission_row.Mission_name} ({mission_row.Points} pts)\n"
        objectives_sorted = sorted(mission_row.Objectives.items(), key=lambda x: x[1])
        for objective, pts in objectives_sorted:
            bold = "**" if mission_row.Points >= pts else ""
            message += f"- {bold}{objective}: {pts} pts{bold}\n"
        return await interaction.followup.send(message)

    @standard_command("Añade una misión de pts de victoria.")
    async def add_mission(
        self: Self,
        interaction: Interaction,
        mission_name: str = SlashOption("nombre-mision", "Nombre de la misión", True),
        objective_name: str = SlashOption(
            "nombre-objetivo", "Nombre del objetivo de puntos. Se pueden añadir mas con /add_objective", True
        ),
        objective_pts: int = SlashOption("pts-objetivo", "Meta de puntos del objetivo", True),
    ) -> None:
        global ACTIVE_MISSION_NAMES
        sh = VictoryPointsController()
        missions = sh.get_all_rows()
        mission_names = [r.Mission_name for r in missions]
        if mission_name in mission_names:
            await interaction.followup.send(f"*{mission_name}* ya está registrado en la lista de misiones.")
        else:

            sh.insert_row(
                VictoryPointsRow(
                    Mission_name=mission_name,
                    Points=0,
                    Objectives={objective_name: objective_pts},
                    Contributions={},
                    Active=1,
                )
            )
            ACTIVE_MISSION_NAMES.append(mission_name)
            await interaction.followup.send(
                f"Se ha añadido la misión *{mission_name}* con el objetivo de {objective_name} ({objective_pts} pts)."
            )

    @standard_command("Añade un objetivo a una misión de pts de victoria.")
    async def add_objective(
        self: Self,
        interaction: Interaction,
        mission_name: str = SlashOption("nombre-mision", "Nombre de la misión", True),
        objective_name: str = SlashOption("nombre-objetivo", "Nombre del objetivo de puntos", True),
        objective_pts: int = SlashOption("pts-objetivo", "Meta de puntos del objetivo", True),
    ) -> None:
        sh = VictoryPointsController()
        mission_row = sh.get_mission_row(mission_name)
        mission_row.change_objective(objective_name, objective_pts)
        sh.set_row(mission_row)
        await interaction.followup.send(f"Se ha añadido el objetivo {objective_name} a la misión *{mission_name}*.")

    @standard_command("Elimina un objetivo de una misión de pts de victoria.")
    async def remove_objective(
        self: Self,
        interaction: Interaction,
        mission_name: str = SlashOption("nombre-mision", "Nombre de la misión", True),
        objective_name: str = SlashOption("nombre-objetivo", "Nombre del objetivo de puntos", True),
    ) -> None:
        sh = VictoryPointsController()
        mission_row = sh.get_mission_row(mission_name)
        mission_row.remove_objective(objective_name)
        sh.set_row(mission_row)
        await interaction.followup.send(f"Se ha eliminado el objetivo {objective_name} de la misión *{mission_name}*.")

    @standard_command("Añade puntos de victoria a una misión.")
    async def victory_points(
        self: Self,
        interaction: Interaction,
        points: int = SlashOption("pts", "Puntos de victoria a añadir (o quitar, si es negativo)", True),
        mission_name: str = SlashOption("nombre-mision", "Nombre de la misión", True),
        target: Member = SlashOption(
            "usuario-target",
            "Usuario cuyo PJ añade los puntos de victoria",
            False,
            default=None,
        ),
    ) -> None:
        user_id: int = target.id if target is not None else interaction.user.id
        sh_vp = VictoryPointsController()
        mission = sh_vp.get_mission_row(mission_name)
        old_total = mission.Points
        old, new = mission.add_points(user_id, points)
        sh_vp.set_row(mission)

        name, contr = mission.user_contribution(user_id)
        return await interaction.followup.send(
            (
                f"{name} {"añade" if points else "quita"} {abs(points)} puntos de victoria a la misión *{mission_name}*.\n"
                f"Total de puntos de victoria: {old_total} -> {mission.Points}\n"
                f"Contribución de {name}: {old} -> {new}"
            )
        )

    @standard_command("Muestra los contribudores a una misión de pts de victoria.")
    async def mission_contributors(
        self: Self,
        interaction: Interaction,
        mission_name: str = SlashOption("nombre-mision", "Nombre de la misión", True),
    ) -> None:
        sh = VictoryPointsController()
        mission_row = sh.get_mission_row(mission_name)
        message = f"**Contribuyentes a la misión:** {mission_row.Mission_name} ({mission_row.Points} pts)\n"
        contributors_sorted = sorted(mission_row.Contributions.items(), key=lambda x: x[1], reverse=True)
        for contributor, pts in contributors_sorted:
            message += f"- {contributor}: {pts} pts\n"
        return await interaction.followup.send(message)

    @add_objective.on_autocomplete("mission_name")
    @mission_details.on_autocomplete("mission_name")
    @remove_objective.on_autocomplete("mission_name")
    @victory_points.on_autocomplete("mission_name")
    @mission_contributors.on_autocomplete("mission_name")
    async def active_mission_names_options(self, interaction: Interaction, input: str) -> Any:
        names = ACTIVE_MISSION_NAMES
        if input:
            names = [name for name in ACTIVE_MISSION_NAMES if input.lower() in name.lower()]
        await interaction.response.send_autocomplete(names)
