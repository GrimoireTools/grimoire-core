from typing import Any, Self

import dndice
import nextcord  # type: ignore
from nextcord.ext import commands  # type: ignore

import SheetControl as sh_pj
import SheetControlSaves as sh_saves
from PF2eData import ABILITIES, PROF, PROF_BONUSES, SAVES, Ability
from SheetControl import PJ_COL, gets_pj_data
from SheetControlSaves import gets_save_data
from utils import CharacterNotFoundError
from varenv import getVar

from .skillUtils import skill_description as save_description, ability_param, format_diceroll, nat_20_1_message

CRI_GUILD_ID = int(getVar("GUILD_ID"))
CODEBLOCK_LANG = "ansi"


class Saves(commands.Cog):
    def __init__(self: Self, client: commands.Bot) -> None:
        self.client = client

    @nextcord.slash_command(
        description="Muestra la información de todas las saves de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_save_data
    async def all_saves(self: Self, interaction: nextcord.Interaction, extra_info: bool = False) -> Any:
        await interaction.response.defer()
        if interaction.user is None:
            return await interaction.followup.send("Error: Null user")
        user_id: int = interaction.user.id
        name_mods, row, pj_mods = sh_saves.get_pj_abilities(user_id)

        if name_mods is None or pj_mods is None:
            return await interaction.followup.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )
        # {save_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_saves = sh_saves.get_pj_saves(user_id)

        message: str = f"# Saves de {name_mods if name is None else name}:\n```{CODEBLOCK_LANG}\n"

        for save_name, mod_type in SAVES:
            if save_name == "Lore":
                continue
            message += save_description(
                pj_mods[mod_type],
                mod_type,
                save_name,
                pj_saves.get(save_name, None),  # type: ignore
                extra_info,
            )

        message += "\n```"
        return await interaction.followup.send(message)

    @nextcord.slash_command(
        description="Muestra la información de una save de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_save_data
    async def save(
        self: Self,
        interaction: nextcord.Interaction,
        save: str = nextcord.SlashOption(
            name="save",
            description="La save de tu personaje",
            required=True,
            choices=[save[0] for save in SAVES if save[0] != "Lore"],
        ),
        extra_info: bool = False,
    ) -> Any:
        await interaction.response.defer()
        if interaction.user is None:
            return await interaction.followup.send("Error: Null user")
        user_id: int = interaction.user.id
        name_mods, row, pj_mods = sh_saves.get_pj_abilities(user_id)

        if name_mods is None or row is None or pj_mods is None:
            return await interaction.followup.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )
        # {save_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_saves = sh_saves.get_pj_saves(user_id)

        message: str = f"## {save} de {name_mods if name is None else name}:\n"

        mod_type: Ability = [ab for save_nm, ab in SAVES if save_nm == save][0]

        message += f"```{CODEBLOCK_LANG}\n{save_description(
            pj_mods[mod_type],
            mod_type,
            save,
            pj_saves.get(save, None),
            extra_info,
        )}```"

        return await interaction.followup.send(message)

    @nextcord.slash_command(
        description="Define la proficiencia de una save de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_save_data
    @gets_pj_data
    async def set_save(
        self: Self,
        interaction: nextcord.Interaction,
        save: str = nextcord.SlashOption(
            name="save",
            description="La save de tu personaje a definir",
            required=True,
            choices=[save[0] for save in SAVES if save[0] != "Lore"],
        ),
        proficiency: str = nextcord.SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la save",
            required=True,
            choices=PROF.profs_list,
        ),
        other_bonuses: int = nextcord.SlashOption(
            name="other_bonuses",
            description="La suma de otros bonos (ni profi ni ability)  (default 0)",
            required=False,
            default=0,
        ),
        other_bonuses_description: str = nextcord.SlashOption(
            name="other_bonuses_description",
            description="Detalle de los otros bonos",
            required=False,
            default="",
        ),
    ) -> Any:
        await interaction.response.defer()
        if interaction.user is None:
            return await interaction.followup.send("Error: Null user")
        user_id: int = interaction.user.id

        pj_name, pj_saves = sh_saves.get_pj_saves(user_id)
        if pj_name is None:
            return await interaction.followup.send("Error: Null character name")

        pj_save = pj_saves.get(save, None)

        if pj_save is None:
            # Create new save entry
            try:
                pj_name = sh_pj.get_pj_data(sh_pj.get_pj_row(user_id), PJ_COL.Name)
            except CharacterNotFoundError as e:
                return await interaction.followup.send(f"{e}")
            row: int = sh_saves.first_empty_save_row()
            msg = f"Se definió la proficiencia de {pj_name} en {save}"
        else:
            # update existing save entry
            row = pj_save["row"]
            msg = f"Se actualizó la proficiencia de {pj_name} en {save}"

        data = (
            pj_name,
            str(user_id),
            save,
            proficiency,
            str(other_bonuses),
            other_bonuses_description,
        )
        sh_saves.update_save_row(row, data)
        return await interaction.followup.send(msg)

    @nextcord.slash_command(
        description="Define las proficiencias de todas las saves de tu personaje",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_save_data
    @gets_pj_data
    async def set_all_saves(
        self: Self,
        interaction: nextcord.Interaction,
        reflex: str = ability_param("reflex"),
        will: str = ability_param("will"),
        fortitude: str = ability_param("fortitude"),
        resilient: str = nextcord.SlashOption(
            name="resilient",
            description="Runa de resiliencia. Si se elije alguna, se sobreescriben los bonos extra. (default No)",
            required=False,
            choices=["No", "Resilient (+1)", "Resilient (Greater) (+2)", "Resilient (Major) (+3)"],
            default="No",
        ),
    ) -> Any:
        await interaction.response.defer()
        if interaction.user is None:
            return await interaction.followup.send("Error: Null user")
        user_id: int = interaction.user.id

        # pj_saves: dict[str, dict[str, str | int]]
        pj_name, pj_saves = sh_saves.get_pj_saves(user_id)

        try:
            pj_name = sh_pj.get_pj_data(sh_pj.get_pj_row(user_id), PJ_COL.Name)
        except CharacterNotFoundError as e:
            return await interaction.followup.send(f"{e}")

        better_args = [
            ("Reflex", reflex),
            ("Will", will),
            ("Fortitude", fortitude),
        ]

        rune = {
            "No": (0, ""),
            "Resilient (+1)": (1, "Resilient"),
            "Resilient (Greater) (+2)": (2, "Resilient (Greater)"),
            "Resilient (Major) (+3)": (3, "Resilient (Major)"),
        }
        resilient_bonus, resilient_description = rune[resilient]

        msg = ""
        rows_and_data = []
        first_empty_row = sh_saves.first_empty_save_row()
        for save_name, prof_value in better_args:
            pj_save = pj_saves.get(save_name, None)

            if pj_save is None:
                # Create new save entry
                row: int = first_empty_row
                msg += f"\nSe definió la proficiencia de {pj_name} en {save_name}"
                first_empty_row += 1
                extra_bonus = resilient_bonus
                extra_description = resilient_description

            else:
                override = resilient != "No"
                # update existing save entry
                row = pj_save["row"]
                msg += f"\nSe actualizó la proficiencia de {pj_name} en {save_name}"
                extra_bonus = resilient_bonus if override else pj_save["extra_bonus"]
                extra_description = resilient_description if override else pj_save["extra_descripcion"]

            data = (
                pj_name,
                str(user_id),
                save_name,
                prof_value,
                extra_bonus,
                extra_description,
            )
            rows_and_data.append((row, data))
        sh_saves.multi_update_save_row(rows_and_data)
        return await interaction.followup.send(msg)

    @nextcord.slash_command(
        description="Tira un save check con el save seleccionado",
        guild_ids=[CRI_GUILD_ID],
    )
    @gets_save_data
    async def roll_save(
        self: Self,
        interaction: nextcord.Interaction,
        save: str = nextcord.SlashOption(
            name="save",
            description="La save de tu personaje que quieres usar",
            required=True,
            choices=[save[0] for save in SAVES if save[0] != "Lore"],
        ),
        extra_modifiers: int = nextcord.SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        await interaction.response.defer()
        if interaction.user is None:
            return await interaction.followup.send("Error: Null user")
        user_id: int = interaction.user.id

        name_mods, row, pj_mods = sh_saves.get_pj_abilities(user_id)

        if name_mods is None or row is None or pj_mods is None:
            return await interaction.followup.send(
                "Tu personaje no tiene modificadores de habilidad definidos. Definelos con /set_modifiers."
            )

        # {save_name: {prof_level: str, extra_bonus: int, extra_descripcion: str}}
        name, pj_saves = sh_saves.get_pj_saves(user_id)

        dice = int(dndice.basic("1d20"))
        nat_20_1: str = nat_20_1_message(dice)

        # ABILITY
        mod_type: Ability = [ab for save_nm, ab in SAVES if save_nm == save][0]
        ability_bonus = pj_mods[mod_type]

        # PROFICIENCY
        pj_save = pj_saves.get(save, None)
        if pj_save is None:
            prof_bonus = 0
        else:
            prof_level: str = pj_save["prof_level"]
            prof_bonus: int = PROF_BONUSES[prof_level]

        # OTHER
        if pj_save is None:
            other_bonus = 0
        else:
            other_bonus: int = pj_save["extra_bonus"]

        total_mod = ability_bonus + prof_bonus + other_bonus + extra_modifiers
        result = dice + total_mod
        save_msg = save_description(
            pj_mods[mod_type],
            mod_type,
            save,
            pj_saves.get(save, None),
            extra_info,
        )
        message = f"# {name_mods} {save} roll: \n```{CODEBLOCK_LANG}\n{save_msg}\n# Resultado: {format_diceroll(dice, result)}\nDetails:[d20{total_mod:+} ({dice})]```"

        return await interaction.followup.send(message)


def setup(client: commands.Bot) -> None:
    client.add_cog(Saves(client))
