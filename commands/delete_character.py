"""
Eliminar un PJ del excel, ya sea completamente, o moviendolo al cementerio.

Pasos:
- Verificar que el personaje exista.
    - Si no existe, enviar un mensaje de error.
- Por default, copiar el personaje a la hoja cementerio. Especificando en el input:
    - Turno de Muerte
    - Narrador de Muerte
    - Causa de muerte
    - Nivel al morir (sacar del nivel global)
- Eliminar:
    - Skills
    - Ability Mods
    - PJ
"""

from typing import Self
from collections.abc import Sequence

from controllers.cemetery_controller import CemeteryController, CemeteryRow
from controllers.lib.cog import standard_command, Cog
from nextcord import Interaction, SlashOption

from controllers.lib.row import Row
from controllers.lib.utils import DataNotFoundError, not_none
from controllers.modifiers_controller import ModifiersController
from controllers.pjs_controller import PJsController
from controllers.saves_controller import SavesController
from controllers.skills_controller import SkillsController


class DeleteCharacterCommands(Cog):
    @standard_command(
        "Manda un PJ al cementerio y elimina sus datos secundarios (skills, mods, etc)"
    )
    async def retire(
        self: Self,
        interaction: Interaction,
        death_turn: int = SlashOption(
            "turno-de-retiro", "Numero de turno en que el PJ fué retirado o murió", True
        ),
        death_narrator: str = SlashOption(
            "narrador-de-muerte", "Narrador responsable de la muerte del PJ", True
        ),
        death_cause: str = SlashOption(
            "causa-de-muerte", "Enemigo o situación causante de la muerte del PJ", True
        ),
        death_level: int = SlashOption(
            "level-alcanzado", "Nivel en que estaba el PJ al morir o retirarse", True
        ),
    ) -> None:
        user_id = not_none(interaction.user).id
        # Eliminar el personaje
        sh_pjs = PJsController()
        pj = sh_pjs.get_pj_row(user_id)
        sh_pjs.delete_row(pj)

        # Copiar el personaje al cementerio
        sh_cemetery = CemeteryController()
        cemetery_row = CemeteryRow.from_pj_row(
            pj, f"T{death_turn}", death_narrator, death_cause, death_level
        )
        sh_cemetery.insert_row(cemetery_row)
        # Eliminar todas las filas de skills
        try:
            sh_skills = SkillsController()
            skills = sh_skills.get_all_prof_rows(user_id)
            index_groups = group_row_indexes(skills)
            for indexes in index_groups:
                sh_skills.delete_rows(min(indexes), max(indexes))
        except DataNotFoundError:
            pass
        # Eliminar todas las filas de saves
        try:
            sh_saves = SavesController()
            saves = sh_saves.get_all_prof_rows(user_id)
            index_groups = group_row_indexes(saves)
            for indexes in index_groups:
                sh_saves.delete_rows(min(indexes), max(indexes))
        except DataNotFoundError:
            pass
        # Eliminar la fila de ability mods
        try:
            sh_mods = ModifiersController()
            mods = sh_mods.get_mods_row(user_id)
            sh_mods.delete_row(mods)
        except DataNotFoundError:
            pass
        # Enviar mensaje de confirmación
        await interaction.followup.send(
            f"El PJ {pj.Name} ha sido retirado del juego y enviado al cementerio."
        )


def group_row_indexes(rows: Sequence[Row]) -> list[list[int]]:
    """Calculates the continous intervals of rows, ignoring -1 indexes."""
    indexes = sorted([r.get_index() for r in rows if r.get_index() != -1])
    if not indexes:
        return []

    result = []
    current_group = [indexes[0]]

    for i in range(1, len(indexes)):
        if indexes[i] == indexes[i - 1] + 1:
            current_group.append(indexes[i])
        else:
            result.append(current_group)
            current_group = [indexes[i]]

    result.append(current_group)
    result.reverse()
    return result
