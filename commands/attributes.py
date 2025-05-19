from typing import Any, Self
from nextcord import Interaction

from commands.utils.skill_utils import *
from controllers.lib.cog import Cog, standard_command
from controllers.lib.utils import DataNotFoundError, not_none
from controllers.pjs_controller import PJsController
from controllers.attributes_controller import AttributesController, AttributesRow

CODEBLOCK_LANG = "ansi"


class AttributesCommands(Cog):

    @standard_command("Define los Ability Scores de tu personaje")
    async def dgm_set_ability_scores(
        self: Self,
        interaction: Interaction,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_mods = AttributesController()
        try:
            mods_row = sh_mods.get_mods_row(user_id)
        except DataNotFoundError:
            mods_row = AttributesRow(
                PJ_name=pj.Name,
                Discord_id=user_id,
            )
        mods_row.STR = strength
        mods_row.DEX = dexterity
        mods_row.CON = constitution
        mods_row.INT = intelligence
        mods_row.WIS = wisdom
        mods_row.CHA = charisma

        sh_mods.update_or_insert(mods_row)
        return await interaction.followup.send(f"Actualizados las ability scores de {pj.Name}: \n{mods_row.pretty()}")
