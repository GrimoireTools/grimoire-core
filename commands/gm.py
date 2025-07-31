"""Discord bot commands for character information and status management."""

from typing import Any, Self
from controllers.gm_controller import GMController, GMRow
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import DataNotFoundError, default_user_option, not_none
from nextcord import Interaction, Member


class GMCommands(Cog):
    """Commands related to character information and status."""

    @standard_command(description="Entrega tu info de GM")
    async def gm_info(self: Self, interaction: Interaction, user: Member = default_user_option) -> Any:
        """Display the GM information for a user."""
        user_id = not_none(interaction.user).id if user is None else user.id
        gm = GMController().get_gm_row(user_id)
        if gm.gm_row_exists(user_id):
            return await interaction.followup.send(
                f"GM Info de {gm.Emoji} {gm.Name}: {gm.Tag_name}, {gm.Notion_mission_tag}"
            )
        else:
            raise DataNotFoundError("No tienes tus datos de GM definidos. Definelos con `/register_gm`.")

    @standard_command("Registra un usuario GM")
    async def register_gm(
        self: Self,
        interaction: Interaction,
        name: str,
        mission_tag: str,
        emoji: str,
        user: Member | None = default_user_option,
    ) -> Any:
        """Register a GM with the bot."""
        user_id = not_none(interaction.user).id if user is None else user.id
        sh = GMController()
        if sh.gm_row_exists(user_id):
            row = sh.get_gm_row(user_id)
            row.Name = name or row.Name
            row.Notion_mission_tag = mission_tag or row.Notion_mission_tag
            row.Discord_id = str(user_id)
            row.Tag_name = user.display_name if user else row.Tag_name

            await interaction.followup.send(f"GM {row.Name} actualizado.")
        else:
            row = GMRow(
                Name=name,
                Discord_id=str(user_id),
                Tag_name=mission_tag,
                Notion_mission_tag="TBI",
                Emoji=emoji,  # Default emoji, can be customized later
            )
            sh.insert_row(row)
            await interaction.followup.send(f"GM {row.Name} registrado.")

        # Here you would implement the logic to register the GM, e.g., collecting data from the user.
        # For now, we will just send a placeholder message.
        await interaction.followup.send("Por favor, proporciona los datos necesarios para registrar tu GM.")
