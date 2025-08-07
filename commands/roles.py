"""
Commands for managing character roles in Pathfinder 2e.

This module defines commands to list and add roles for Pathfinder 2e characters
"""

from typing import Any, Self
from loguru import logger
from nextcord import Interaction, SlashOption, Member

from controllers.lib.row import JsonData
from controllers.pjs_controller import get_cached_name
from controllers.roles_controller import RolesController, ROLES, RolesRow
from controllers.lib.cog import standard_command, Cog
from controllers.lib.utils import default_user_option


class RolesCommands(Cog):
    """Commands for managing character roles in Pathfinder 2e."""

    @standard_command("Muestra la lista de tus roles")
    async def roles(
        self: Self,
        interaction: Interaction,
        target: Member = default_user_option,
    ) -> Any:
        """Display the roles known by the specified player or the command issuer."""
        user_id: int = target.id if target is not None else interaction.user.id
        roles = RolesController().get_roles_row(user_id).roles_list()
        if roles:
            role_list = "\n- ".join(f"{ROLES[role]} {role}" for role in roles)
            message = f"**Roles de {get_cached_name(user_id)}:**\n- {role_list}"
        else:
            message = f"{get_cached_name(user_id)} no tiene roles asignados."
        return await interaction.followup.send(message)

    @standard_command("Añade un rol a la lista de tu PJ")
    async def setrole(
        self: Self,
        interaction: Interaction,
        addedrole: str = SlashOption("rol", "Rol que quieres añadir a tu PJ", True, choices=list(ROLES)),
        target: Member = default_user_option,
    ) -> Any:
        """Add a new role to the character's known roles."""
        user_id: int = target.id if target else interaction.user.id
        logger.debug(f"Adding role {addedrole} for user {user_id}")
        sh = RolesController()
        if sh.roles_row_exists(user_id):
            logger.debug(f"Roles row exists for user {user_id}, fetching existing roles")
            row = sh.get_roles_row(user_id)
        else:
            logger.debug(f"Roles row does not exist for user {user_id}, creating new row")
            row = RolesRow(PJ_name=get_cached_name(user_id), Discord_id=str(user_id), Roles=JsonData[int, str]())

        logger.debug(f"Current roles for user {user_id}: {row}")

        roles = row.roles_list()

        if addedrole not in roles:
            roles.append(addedrole)
            row.Roles = JsonData(roles)
            sh.update_or_insert(row)
            return await interaction.followup.send(
                f"`{ROLES[addedrole]} {addedrole}` ha sido añadido a la lista de {get_cached_name(user_id)}."
            )
        else:
            roles.remove(addedrole)
            row.Roles = JsonData(roles)
            sh.update_or_insert(row)
            return await interaction.followup.send(
                f"`{ROLES[addedrole]} {addedrole}` ya está en tu lista. Se eliminará de tu lista."
            )
