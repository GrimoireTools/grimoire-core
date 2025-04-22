from typing import Any, Self

from nextcord import Interaction, Member, SlashOption
from controllers.consent_form_controller import ConsentFormController
from controllers.lib.cog import Cog, standard_command


def player(x: int) -> SlashOption:
    """
    Returns a SlashOption for a player.
    """
    return SlashOption(f"jugador_{x}", required=False, default=None)


class ConsentFormCommands(Cog):

    @standard_command("Muestra las respuestas del formulario de consentimiento y avisa a quienes no la han rellenado")
    async def consent_form(
        self: Self,
        interaction: Interaction,
        player_1: Member = player(1),
        player_2: Member = player(2),
        player_3: Member = player(3),
        player_4: Member = player(4),
        player_5: Member = player(5),
    ) -> Any:
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
                    f"{player.mention}, no has rellenado el [formulario de consentimiento](https://forms.gle/QBEYg4g3ymenvbFw8). Por favor, rellenalo. Tu id de discord es: `{player.id}`."
                )
            else:
                notable_options = response.notable_options()
                if len(notable_options) > 0:
                    triggers.append(f"Los triggers de {player.nick} son:\n- {"\n- ".join(notable_options)}")
                else:
                    triggers.append(f"{player.nick} no tiene triggers en el formulario de consentimiento.")

        for msg in triggers:
            await interaction.followup.send(msg, ephemeral=True)
