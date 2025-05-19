from typing import Any, Self
from nextcord import Interaction, SlashOption

import dndice
from system_data import ATTRS, ROLL, ROLL_TYPES, Prof, Attr, PROFS_LIST, ATTRS_LIST, RollType, d20
from commands.utils.skill_utils import *
from controllers.lib.cog import Cog, standard_command
from controllers.lib.utils import DataNotFoundError, not_none
from controllers.pjs_controller import PJsController
from controllers.saves_controller import SavesController
from controllers.attributes_controller import AttributesController, AttributesRow

CODEBLOCK_LANG = "ansi"


class SaveCommands(Cog):

    @standard_command("Muestra la información de todas las saves de tu personaje")
    async def dgm_all_saves(self: Self, interaction: Interaction, extra_info: bool = False) -> Any:
        user_id = not_none(interaction.user).id
        mods_row = AttributesController().get_mods_row(user_id)
        all_save_rows = SavesController().get_all_prof_rows(user_id)

        message: str = f"# Saves de {mods_row.PJ_name}:\n```{CODEBLOCK_LANG}\n"

        for save_row in all_save_rows:
            mod_type = save_row.mod_type()
            message += skill_description(
                mods_row[mod_type],
                mod_type,
                save_row.Save_name,
                save_row,
                extra_info,
            )
        message += "\n```"
        return await interaction.followup.send(message)

    @standard_command("Muestra la información de una save de tu personaje")
    async def dgm_save(
        self: Self,
        interaction: Interaction,
        save_name: Attr = SlashOption(
            name="save",
            description="La save de tu personaje",
            required=True,
            choices=ATTRS_LIST,
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id = not_none(interaction.user).id
        mod_type = save_name
        mods_row = AttributesController().get_mods_row(user_id)
        save_row = SavesController().get_prof_row(user_id, save_name)

        message: str = f"## {save_name} de {mods_row.PJ_name}:\n"
        message += f"```{CODEBLOCK_LANG}\n{skill_description(
            mods_row[mod_type],
            mod_type,
            save_name,
            save_row,
            extra_info,
        )}```"

        return await interaction.followup.send(message)

    @standard_command("Define la proficiencia de una save de tu personaje")
    async def dgm_set_save(
        self: Self,
        interaction: Interaction,
        save: Attr = SlashOption(
            name="save",
            description="La save de tu personaje a definir",
            required=True,
            choices=ATTRS_LIST,
        ),
        proficiency: str = SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la save",
            required=True,
            choices=PROFS_LIST,
        ),
        other_bonuses: int = SlashOption(
            name="other_bonuses",
            description="La suma de otros bonos (ni profi ni ability)  (default 0)",
            required=False,
            default=0,
        ),
        other_bonuses_description: str = SlashOption(
            name="other_bonuses_description",
            description="Detalle de los otros bonos",
            required=False,
            default="",
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_saves = SavesController()
        save_row = sh_saves.get_prof_row(user_id, save)

        new_row = SaveRow(
            PJ_name=pj.Name,
            Discord_id=user_id,
            Save_name=save,
            Proficiency=proficiency,
            Extra_bonus=other_bonuses,
            Bonus_description=other_bonuses_description,
        )

        if save_row is None:
            msg = f"Se definió la proficiencia de {pj.Name} en {save}"
        else:
            msg = f"Se actualizó la proficiencia de {pj.Name} en {save}"
            new_row.set_index(save_row.get_index())

        sh_saves.update_or_insert(new_row)
        return await interaction.followup.send(msg)

    @standard_command("Define las proficiencias de todas las saves de tu personaje")
    async def dgm_set_all_saves(
        self: Self,
        interaction: Interaction,
        strength: Prof = ability_param("Strength"),
        dexterity: Prof = ability_param("dexterity"),
        constitution: Prof = ability_param("constitution"),
        intelligence: Prof = ability_param("intelligence"),
        wisdom: Prof = ability_param("wisdom"),
        charisma: Prof = ability_param("charisma"),
        global_bonus: int = SlashOption(
            "bono_base", "Bono global a las saves (para no tener que definirlo uno a uno)", default=0, required=False
        ),
        global_bonus_desc: str = SlashOption(
            "bono_base_desc", "Descripción del bono global a las saves", default="", required=False
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_saves = SavesController()

        proficiencies: list[tuple[Attr, Prof]] = [
            (ATTRS.STR, strength),
            (ATTRS.DEX, dexterity),
            (ATTRS.CON, constitution),
            (ATTRS.INT, intelligence),
            (ATTRS.WIS, wisdom),
            (ATTRS.CHA, charisma),
        ]

        msg = ""
        rows = []
        for save_name, prof_value in proficiencies:
            pj_save = sh_saves.get_prof_row(user_id, save_name)

            if pj_save is None:
                # Create new save entry
                msg += f"\nSe definió la proficiencia de {pj.Name} en {save_name}"
                row = SaveRow(
                    PJ_name=pj.Name,
                    Discord_id=user_id,
                    Save_name=save_name,
                    Proficiency=prof_value,
                    Extra_bonus=global_bonus,
                    Bonus_description=global_bonus_desc,
                )
            else:
                # update existing save entry
                msg += f"\nSe actualizó la proficiencia de {pj.Name} en {save_name}"
                pj_save.Proficiency = prof_value
                pj_save.Extra_bonus = global_bonus
                pj_save.Bonus_description = global_bonus_desc
                row = pj_save
            rows.append(row)
        sh_saves.update_or_insert_batch(rows)
        return await interaction.followup.send(msg)

    @standard_command("Tira un save check con el save seleccionado")
    async def dgm_roll_save(
        self: Self,
        interaction: Interaction,
        save: Attr = SlashOption(
            name="save",
            description="La save de tu personaje que quieres usar",
            required=True,
            choices=ATTRS_LIST,
        ),
        advantage: RollType = SlashOption(
            name="ventaja",
            description="Si la tirada tiene ventaja o desventaja",
            required=False,
            default=ROLL.NORMAL,
            choices=ROLL_TYPES,
        ),
        extra_modifiers: int = SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id = not_none(interaction.user).id

        message = save_roll_message(user_id, save, extra_modifiers, extra_info, advantage)

        return await interaction.followup.send(message)


def save_roll_message(
    user_id: int, save_name: Attr, extra_mod: int = 0, extra_info: bool = False, advantage: RollType = ROLL.NORMAL
) -> str:
    mods_row = AttributesController().get_mods_row(user_id)
    save_row = SavesController().get_prof_row(user_id, save_name)

    dice = d20(advantage)

    # ABILITY
    ability_bonus = mods_row[save_name]

    # PROFICIENCY
    if save_row is None:
        prof_bonus = 0
        other_bonus = 0
    else:
        prof_bonus = save_row.prof_bonus()
        other_bonus = not_none(save_row.Extra_bonus)

    total_mod = ability_bonus + prof_bonus + other_bonus + extra_mod
    result = dice + total_mod
    save_msg = skill_description(
        ability_bonus,
        save_name,
        save_name,
        save_row,
        extra_info,
    )
    return f"# {mods_row.PJ_name} {save_name} roll: \n```{CODEBLOCK_LANG}\n{save_msg}\n# Resultado: {format_diceroll(dice, result)}\nDetails:[d20{total_mod:+} ({dice})]```"
