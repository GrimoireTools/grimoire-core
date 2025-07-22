"""Commands for managing player consent forms.

This module provides Discord slash commands for checking consent form responses
and notifying players who haven't completed the required forms. It handles
player mentions and displays consent-related triggers privately to moderators.
"""

from typing import Any, Self

from nextcord import Interaction, Member, SlashOption
from controllers.consent_form_controller import ConsentFormController
from controllers.lib.cog import Cog, standard_command


def player(x: int) -> SlashOption:
    """Make a default SlashOption for a player."""
    return SlashOption(f"jugador_{x}", required=False, default=None)


PLAYER_1 = player(1)
PLAYER_2 = player(2)
PLAYER_3 = player(3)
PLAYER_4 = player(4)
PLAYER_5 = player(5)


class ConsentFormCommands(Cog):
    """Commands related to the consent form for players."""

    @standard_command("Muestra las respuestas del formulario de consentimiento y avisa a quienes no la han rellenado")
    async def consent_form(
        self: Self,
        interaction: Interaction,
        player_1: Member = PLAYER_1,
        player_2: Member = PLAYER_2,
        player_3: Member = PLAYER_3,
        player_4: Member = PLAYER_4,
        player_5: Member = PLAYER_5,
    ) -> Any:
        """Check consent form responses for specified players and notify those who haven't completed it."""
        r = interaction.followup.send(
            "Buscando respuestas del formulario de consentimiento. Esto puede tardar unos segundos..."
        )
        sh = ConsentFormController()
        players = [player_1, player_2, player_3, player_4, player_5]
        players = [p for p in players if p is not None]

        triggers = []
        await r
        if len(players) == 0:
            return await interaction.followup.send("No has mencionado a ningun jugador.")

        for player in players:
            response = sh.get_latest_response(player.id)
            if response is None:
                await interaction.followup.send(
                    f"{player.mention}, no has rellenado el [formulario de consentimiento]"
                    f"(https://forms.gle/QBEYg4g3ymenvbFw8). Por favor, rellenalo. "
                    f"Tu id de discord es: `{player.id}`."
                )
            else:
                notable_options = response.notable_options()
                if len(notable_options) > 0:
                    triggers.append(f"Los triggers de {player.nick} son:\n- {'\n- '.join(notable_options)}")
                else:
                    triggers.append(f"{player.nick} no tiene triggers en el formulario de consentimiento.")

        for msg in triggers:
            await interaction.followup.send(msg, ephemeral=True)
