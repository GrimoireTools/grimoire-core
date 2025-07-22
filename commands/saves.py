"""Commands for managing character saves."""

from typing import Any, Self
from nextcord import Interaction, SlashOption

import dndice
from PF2eData import PROF, SAVES, Prof, Save
from commands.utils.skill_utils import ability_param, skill_description, format_diceroll
from controllers.lib.cog import Cog, standard_command
from controllers.lib.utils import not_none
from controllers.pjs_controller import PJsController
from controllers.saves_controller import SaveRow, SavesController, save_mod_type
from controllers.modifiers_controller import ModifiersController

CODEBLOCK_LANG = "ansi"


class SaveCommands(Cog):
    """Commands for managing character saves."""

    @standard_command("Muestra la información de todas las saves de tu personaje")
    async def all_saves(self: Self, interaction: Interaction, extra_info: bool = False) -> Any:
        """Display all saves of the character."""
        user_id = not_none(interaction.user).id
        mods_row = ModifiersController().get_mods_row(user_id)
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
                user_id,
            )
        message += "\n```"
        return await interaction.followup.send(message)

    @standard_command("Muestra la información de una save de tu personaje")
    async def save(
        self: Self,
        interaction: Interaction,
        save_name: Save = SlashOption(
            name="save",
            description="La save de tu personaje",
            required=True,
            choices=[save[0] for save in SAVES],
        ),
        extra_info: bool = False,
    ) -> Any:
        """Display information about a specific save of the character."""
        user_id = not_none(interaction.user).id
        mod_type = save_mod_type(save_name)
        mods_row = ModifiersController().get_mods_row(user_id)
        save_row = SavesController().get_prof_row(user_id, save_name)

        message: str = f"## {save_name} de {mods_row.PJ_name}:\n"
        message += f"```{CODEBLOCK_LANG}\n{
            skill_description(mods_row[mod_type], mod_type, save_name, save_row, extra_info, user_id)
        }```"

        return await interaction.followup.send(message)

    @standard_command("Define la proficiencia de una save de tu personaje")
    async def set_save(
        self: Self,
        interaction: Interaction,
        save: Save = SlashOption(
            name="save",
            description="La save de tu personaje a definir",
            required=True,
            choices=[save[0] for save in SAVES],
        ),
        proficiency: Prof = SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la save",
            required=True,
            choices=PROF.profs_list,
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
        """Define the proficiency of a specific save for the character."""
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
    async def set_all_saves(
        self: Self,
        interaction: Interaction,
        fortitude: Prof = ability_param("fortitude"),
        reflex: Prof = ability_param("reflex"),
        will: Prof = ability_param("will"),
        resilient: str = SlashOption(
            name="resilient",
            description="Runa de resiliencia. Sobreescribe bonos extra. (default No)",
            required=False,
            choices=["No", "Resilient (+1)", "Resilient (Greater) (+2)", "Resilient (Major) (+3)"],
            default="No",
        ),
    ) -> Any:
        """Define the proficiencies of all saves for the character."""
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_saves = SavesController()

        proficiencies: dict[Save, Prof] = {
            "Fortitude": fortitude,
            "Reflex": reflex,
            "Will": will,
        }

        rune = {
            "No": (0, ""),
            "Resilient (+1)": (1, "Resilient"),
            "Resilient (Greater) (+2)": (2, "Resilient (Greater)"),
            "Resilient (Major) (+3)": (3, "Resilient (Major)"),
        }
        resilient_bonus, resilient_description = rune[resilient]

        msg = ""
        rows = []
        for save_name, prof_value in proficiencies.items():
            pj_save = sh_saves.get_prof_row(user_id, save_name)

            if pj_save is None:
                # Create new save entry
                msg += f"\nSe definió la proficiencia de {pj.Name} en {save_name}"
                row = SaveRow(
                    PJ_name=pj.Name,
                    Discord_id=user_id,
                    Save_name=save_name,
                    Proficiency=prof_value,
                    Extra_bonus=resilient_bonus,
                    Bonus_description=resilient_description,
                )
            else:
                # update existing save entry
                msg += f"\nSe actualizó la proficiencia de {pj.Name} en {save_name}"
                pj_save.Proficiency = prof_value
                override = resilient != "No"
                pj_save.Extra_bonus = resilient_bonus if override else pj_save.Extra_bonus
                pj_save.Bonus_description = resilient_description if override else pj_save.Bonus_description
                row = pj_save
            rows.append(row)
        sh_saves.update_or_insert_batch(rows)
        return await interaction.followup.send(msg)

    @standard_command("Tira un save check con el save seleccionado")
    async def roll_save(
        self: Self,
        interaction: Interaction,
        save: Save = SlashOption(
            name="save",
            description="La save de tu personaje que quieres usar",
            required=True,
            choices=[save[0] for save in SAVES],
        ),
        extra_modifiers: int = SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        """Roll a save check with the selected save."""
        user_id = not_none(interaction.user).id

        message = save_roll_message(
            user_id,
            save,
            extra_modifiers,
            extra_info,
        )

        return await interaction.followup.send(message)


def save_roll_message(user_id: int, save_name: Save, extra_mod: int = 0, extra_info: bool = False) -> str:
    """Generate a message for a save roll."""
    mods_row = ModifiersController().get_mods_row(user_id)
    save_row = SavesController().get_prof_row(user_id, save_name)

    dice = int(dndice.basic("1d20"))

    # ABILITY
    mod_type: str = save_mod_type(save_name)
    ability_bonus = mods_row[mod_type]

    # PROFICIENCY
    if save_row is None:
        prof_bonus = 0
        other_bonus = 0
    else:
        prof_bonus = save_row.prof_bonus()
        other_bonus = not_none(save_row.Extra_bonus)

    total_mod = ability_bonus + prof_bonus + other_bonus + extra_mod
    result = dice + total_mod
    save_msg = skill_description(ability_bonus, mod_type, save_name, save_row, extra_info, user_id, extra_mod)
    return (
        f"# {mods_row.PJ_name} {save_name} roll: \n"
        f"```{CODEBLOCK_LANG}\n"
        f"{save_msg}\n"
        f"# Resultado: {format_diceroll(dice, result)}\n"
        f"Details:[d20{total_mod:+} ({dice})]```"
    )
