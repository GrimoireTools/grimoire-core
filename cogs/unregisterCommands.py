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
    - Reputación
    - Skills
    - Ability Mods
    - PJ
"""

from typing import Any, Callable, Self

import nextcord  # type: ignore
from nextcord.ext import commands

import SheetControl as sh
from SheetControl import PJ_COL, gets_pj_data
from SheetControlCemetery import gets_cemetery_data, add_dead_PJ
from utils import CharacterNotFoundError
from varenv import getVar

CRI_GUILD_ID = int(getVar("GUILD_ID"))


class Unregister(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @gets_cemetery_data
    @gets_pj_data
    async def retire(
        self: Self,
        interaction: nextcord.Interaction,
        death_turn: int = nextcord.SlashOption(
            "turno-de-retiro", "Numero de turno en que el PJ fué retirado o murió", True
        ),
        death_narrator: str = nextcord.SlashOption(
            "narrador-de-muerte", "Narrador responsable de la muerte del PJ", True
        ),
        death_cause: str = nextcord.SlashOption(
            "causa-de-muerte", "Enemigo o situación causante de la muerte del PJ", True
        ),
        death_level: int = nextcord.SlashOption(
            "level-alcanzado", "Nivel en que estaba el PJ al morir o retirarse", True
        ),
    ):
        await interaction.response.defer()
        if interaction.user is None:
            return await interaction.followup.send("Error: Null user")
        user_id: int = interaction.user.id
        try:
            pj_row = sh.get_pj_row(user_id)
            pj_name = sh.get_pj_data(pj_row, PJ_COL.Name)
        except CharacterNotFoundError:
            return await interaction.followup.send("No se encontró un personaje con ID de discord correspondiente")

        pj_row_data = sh.get_pj_full(pj_row)

        # Copiar el personaje al cementerio
        add_dead_PJ(pj_row_data, death_turn, death_narrator, death_cause, death_level)
        # Eliminar el personaje
        sh.delete_row(pj_row)

        # Eliminar todas las filas de reputación

        # Eliminar todas las filas de skills

        # Eliminar todas las filas de ability mods
