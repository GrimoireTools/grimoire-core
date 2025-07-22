"""
Provides slash commands for managing and displaying character languages.

This module defines commands to list and add languages for Pathfinder 2e characters
using Discord interactions. It includes the LanguagesCommands cog with commands
to show a user's known languages and to add new languages to their character.

Important classes/functions:
    - LanguagesCommands: Cog containing language management commands.
"""

from typing import Any, Self
from nextcord import Interaction, SlashOption, Member

from PF2eData import LANGUAGES
from controllers.pjs_controller import PJsController
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option


class LanguagesCommands(Cog):
    """Commands for managing character languages in Pathfinder 2e."""

    @standard_command("Muestra la lista de tus lenguajes")
    async def languages(
        self: Self,
        interaction: Interaction,
        target: Member = default_user_option,
    ) -> Any:
        """Display the languages known by the specified player or the command issuer."""
        user_id: int = target.id if target is not None else interaction.user.id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        if pj.Languages not in [None, ""]:
            languages = pj.Languages.split(", ")
            language_list = "\n- ".join(languages)
            message = f"**Lenguajes de {pj.Name}:**\n- {language_list}"
        else:
            message = f"{pj.Name} no sabe ningún lenguaje."
        return await interaction.followup.send(message)

    @standard_command("Añade un lenguaje a la lista de tu PJ")
    async def addlanguage(
        self: Self,
        interaction: Interaction,
        addedlanguage: str = SlashOption("lenguaje", "Lenguaje que quieres añadir a tu PJ", True, choices=LANGUAGES),
        target: Member = default_user_option,
    ) -> Any:
        """Add a new language to the character's known languages."""
        user_id: int = target.id if target is not None else interaction.user.id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)

        if addedlanguage not in pj.Languages:
            pj.add_language(addedlanguage)
            sh.update_row(pj)
            return await interaction.followup.send(f"{addedlanguage} ha sido añadido a la lista de {pj.Name}.")
        else:
            return await interaction.followup.send(f"{addedlanguage} ya está en la lista de {pj.Name}.")
