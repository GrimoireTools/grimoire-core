"""Commands for managing character skills in a Pathfinder 2e game."""

from typing import Any, Self
from nextcord import Interaction, SlashOption

import dndice
from PF2eData import LORELESS_SKILLS, PROF, Prof, Skill
from commands.utils.skill_utils import ability_param, skill_description, format_diceroll, filter_lores
from controllers.lib.cog import Cog, standard_command
from controllers.lib.utils import DataNotFoundError, not_none
from controllers.lvl_groups_controller import LEVEL_GROUPS, LevelGroup
from controllers.pjs_controller import PJsController, get_cached_group
from controllers.skills_controller import SkillRow, SkillsController, skill_mod_type
from controllers.modifiers_controller import ModifiersController, ModifiersRow

CODEBLOCK_LANG = "ansi"


class SkillCommands(Cog):
    """Commands for managing character skills."""

    @standard_command("Muestra la información de todas las skills de tu personaje")
    async def all_skills(self: Self, interaction: Interaction, extra_info: bool = False) -> Any:
        """Display all skills of the character."""
        user_id = not_none(interaction.user).id
        mods_row = ModifiersController().get_mods_row(user_id)
        all_skill_rows = SkillsController().get_all_prof_rows(user_id)

        message: str = f"# Skills de {mods_row.PJ_name}:\n```{CODEBLOCK_LANG}\n"

        for skill_row in [sk for sk in all_skill_rows if not sk.is_lore()]:
            mod_type = skill_row.mod_type()
            message += skill_description(
                mods_row[mod_type], mod_type, skill_row.Skill_name, skill_row, extra_info, user_id
            )
        message += "\n```"
        return await interaction.followup.send(message)

    @standard_command("Muestra la información de todas las lore skills de tu personaje")
    async def all_lores(self: Self, interaction: Interaction, extra_info: bool = False) -> Any:
        """Display all lore skills of the character."""
        user_id = not_none(interaction.user).id
        mods_row = ModifiersController().get_mods_row(user_id)
        all_skill_rows = SkillsController().get_all_prof_rows(user_id)

        message: str = f"# Skills de {mods_row.PJ_name}:\n```{CODEBLOCK_LANG}\n"

        for skill_row in [sk for sk in all_skill_rows if sk.is_lore()]:
            mod_type = "Int"
            message += skill_description(
                mods_row[mod_type], mod_type, skill_row.Skill_name, skill_row, extra_info, user_id
            )
        message += "\n```"
        return await interaction.followup.send(message)

    @standard_command("Muestra la información de una skill de tu personaje")
    async def skill(
        self: Self,
        interaction: Interaction,
        skill_name: Skill = SlashOption(
            name="skill",
            description="La skill de tu personaje",
            required=True,
            choices=LORELESS_SKILLS,
        ),
        extra_info: bool = False,
    ) -> Any:
        """Display information about a specific skill of the character."""
        user_id = not_none(interaction.user).id
        mod_type = skill_mod_type(skill_name)
        mods_row = ModifiersController().get_mods_row(user_id)
        skill_row = SkillsController().get_prof_row(user_id, skill_name)

        message: str = f"## {skill_name} de {mods_row.PJ_name}:\n"
        message += f"```{CODEBLOCK_LANG}\n{
            skill_description(mods_row[mod_type], mod_type, skill_name, skill_row, extra_info, user_id)
        }```"

        return await interaction.followup.send(message)

    @standard_command("Muestra la información de una skill de lore de tu personaje")
    async def lore(
        self: Self,
        interaction: Interaction,
        lore_subname: str = SlashOption(
            name="lore",
            description="El lore de tu personaje (sin 'Lore ')",
            required=True,
        ),
        extra_info: bool = False,
    ) -> Any:
        """Display information about a specific lore skill of the character."""
        skill_name = f"Lore ({lore_subname})"

        user_id = not_none(interaction.user).id
        mod_type = skill_mod_type(skill_name)
        mods_row = ModifiersController().get_mods_row(user_id)
        skill_row = SkillsController().get_prof_row(user_id, skill_name)

        message: str = f"## {skill_name} de {mods_row.PJ_name}:\n"
        message += f"```{CODEBLOCK_LANG}\n{
            skill_description(mods_row[mod_type], mod_type, skill_name, skill_row, extra_info, user_id)
        }```"

        return await interaction.followup.send(message)

    @standard_command("Define la proficiencia de una skill de tu personaje")
    async def set_skill(
        self: Self,
        interaction: Interaction,
        skill: Skill = SlashOption(
            name="skill",
            description="La skill de tu personaje a definir",
            required=True,
            choices=LORELESS_SKILLS,
        ),
        proficiency: Prof = SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la skill",
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
        """Define the proficiency of a specific skill for the character."""
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_skills = SkillsController()
        skill_row = sh_skills.get_prof_row(user_id, skill)

        new_row = SkillRow(
            PJ_name=pj.Name,
            Discord_id=user_id,
            Skill_name=skill,
            Proficiency=proficiency,
            Extra_bonus=other_bonuses,
            Bonus_description=other_bonuses_description,
        )

        if skill_row is None:
            msg = f"Se definió la proficiencia de {pj.Name} en {skill}"
        else:
            msg = f"Se actualizó la proficiencia de {pj.Name} en {skill}"
            new_row.set_index(skill_row.get_index())

        sh_skills.update_or_insert(new_row)
        return await interaction.followup.send(msg)

    @standard_command("Define las proficiencias de todas las skills de tu personaje")
    async def set_all_skills(
        self: Self,
        interaction: Interaction,
        perception: Prof = ability_param("perception"),
        acrobatics: Prof = ability_param("acrobatics"),
        arcana: Prof = ability_param("arcana"),
        athletics: Prof = ability_param("athletics"),
        crafting: Prof = ability_param("crafting"),
        deception: Prof = ability_param("deception"),
        diplomacy: Prof = ability_param("diplomacy"),
        intimidation: Prof = ability_param("intimidation"),
        medicine: Prof = ability_param("medicine"),
        nature: Prof = ability_param("nature"),
        occultism: Prof = ability_param("occultism"),
        performance: Prof = ability_param("performance"),
        religion: Prof = ability_param("religion"),
        society: Prof = ability_param("society"),
        stealth: Prof = ability_param("stealth"),
        survival: Prof = ability_param("survival"),
        thievery: Prof = ability_param("thievery"),
    ) -> Any:
        """Define the proficiencies of all skills for the character."""
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_skills = SkillsController()

        proficiencies: dict[Skill, Prof] = {
            "Perception": perception,
            "Acrobatics": acrobatics,
            "Arcana": arcana,
            "Athletics": athletics,
            "Crafting": crafting,
            "Deception": deception,
            "Diplomacy": diplomacy,
            "Intimidation": intimidation,
            "Medicine": medicine,
            "Nature": nature,
            "Occultism": occultism,
            "Performance": performance,
            "Religion": religion,
            "Society": society,
            "Stealth": stealth,
            "Survival": survival,
            "Thievery": thievery,
        }

        msg = ""
        rows = []
        for skill_name, prof_value in proficiencies.items():
            pj_skill = sh_skills.get_prof_row(user_id, skill_name)

            if pj_skill is None:
                # Create new skill entry
                msg += f"\nSe definió la proficiencia de {pj.Name} en {skill_name}"
                row = SkillRow(
                    PJ_name=pj.Name,
                    Discord_id=user_id,
                    Skill_name=skill_name,
                    Proficiency=prof_value,
                    Extra_bonus=0,
                    Bonus_description="",
                )
            else:
                # update existing skill entry
                msg += f"\nSe actualizó la proficiencia de {pj.Name} en {skill_name}"
                pj_skill.Proficiency = prof_value
                row = pj_skill
            rows.append(row)
        sh_skills.update_or_insert_batch(rows)
        return await interaction.followup.send(msg)

    @standard_command("Define la proficiencia de una skill de lore de tu personaje")
    async def set_lore(
        self: Self,
        interaction: Interaction,
        lore_subname: str = SlashOption(
            name="lore_name",
            description="El nombre del lore (sin 'Lore')",
            required=True,
        ),
        proficiency: Prof = SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la skill",
            required=True,
            choices=PROF.profs_list,
        ),
        other_bonuses: int = SlashOption(
            name="other_bonuses",
            description="La suma de otros bonos (ni profi ni ability) (default 0)",
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
        """Define the proficiency of a specific lore skill for the character."""
        user_id = not_none(interaction.user).id
        skill = f"Lore ({lore_subname})"

        pj = PJsController().get_pj_row(user_id)
        sh_skills = SkillsController()
        skill_row = sh_skills.get_prof_row(user_id, skill)

        new_row = SkillRow(
            PJ_name=pj.Name,
            Discord_id=user_id,
            Skill_name=skill,
            Proficiency=proficiency,
            Extra_bonus=other_bonuses,
            Bonus_description=other_bonuses_description,
        )

        if skill_row is None:
            msg = f"Se definió la proficiencia de {pj.Name} en {skill}"
        else:
            msg = f"Se actualizó la proficiencia de {pj.Name} en {skill}"
            new_row.set_index(skill_row.get_index())

        sh_skills.update_or_insert(new_row)
        return await interaction.followup.send(msg)

    @standard_command("Define los modificadores de habilidad de tu personaje")
    async def set_modifiers(
        self: Self,
        interaction: Interaction,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ) -> Any:
        """Define the ability modifiers for the character."""
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_mods = ModifiersController()
        try:
            mods_row = sh_mods.get_mods_row(user_id)
        except DataNotFoundError:
            mods_row = ModifiersRow(
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
        return await interaction.followup.send(f"Actualizados los modificadores de habilidad de {pj.Name}")

    @standard_command("Tira un skill check con el skill seleccionado")
    async def roll_skill(
        self: Self,
        interaction: Interaction,
        skill: Skill = SlashOption(
            name="skill",
            description="La skill de tu personaje que quieres usar",
            required=True,
            choices=LORELESS_SKILLS,
        ),
        extra_modifiers: int = SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        """Roll a skill check with the selected skill."""
        user_id = not_none(interaction.user).id

        message = skill_roll_message(
            user_id,
            skill,
            extra_modifiers,
            extra_info,
        )

        return await interaction.followup.send(message)

    @standard_command("Tira un lore skill check con el lore skill seleccionado")
    async def roll_lore(
        self: Self,
        interaction: Interaction,
        lore_subname: str = SlashOption(
            name="lore",
            description="El lore de tu personaje (sin 'Lore ')",
            required=True,
        ),
        extra_modifiers: int = SlashOption(
            name="extra_modifiers",
            description="Cualquier bono o penalización adicional para esta tirada",
            required=False,
            default=0,
        ),
        extra_info: bool = False,
    ) -> Any:
        """Roll a lore skill check with the selected lore skill."""
        skill = f"Lore ({lore_subname})"
        user_id = not_none(interaction.user).id

        message = skill_roll_message(
            user_id,
            skill,
            extra_modifiers,
            extra_info,
        )

        return await interaction.followup.send(message)

    @standard_command("Muestra los primeros n PJs con la mejor skill seleccionada")
    async def skill_ranking(
        self: Self,
        interaction: Interaction,
        skill: Skill = SlashOption(
            name="skill",
            description="La skill de tu personaje que quieres usar",
            required=True,
            choices=LORELESS_SKILLS,
        ),
        n: int = SlashOption(
            name="n",
            description="Cantidad de PJs a mostrar",
            required=False,
            default=5,
            min_value=1,
        ),
        group: LevelGroup = SlashOption(
            name="level_group",
            description="El grupo de nivel al que pertenecen los PJs",
            required=False,
            default=None,
            choices=LEVEL_GROUPS,
        ),
    ) -> Any:
        """Display the top n characters with the best selected skill."""
        sh_skills = SkillsController()
        sh_mods = ModifiersController()
        if group is None:
            user_id = not_none(interaction.user).id
            group = get_cached_group(user_id)

        all_skills: list[SkillRow] = sh_skills.find_rows_with_values(
            {
                "Skill_name": skill,
            }
        )

        all_skills = [sk for sk in all_skills if get_cached_group(sk.Discord_id) == group]
        if not all_skills:
            return await interaction.followup.send(f"No hay PJs con la skill {skill} en el grupo {group}.")
        all_bonuses = [
            (sk.PJ_name, sk.Proficiency, sk.total_bonus(sh_mods.get_mods_row(int(sk.Discord_id))))
            for sk in all_skills
            if sk is not None and sh_mods.mods_row_exists(int(sk.Discord_id))
        ]
        sorted_bonuses = sorted(all_bonuses, key=lambda x: x[2], reverse=True)
        message: str = f"# Ranking de {skill}:\n```{CODEBLOCK_LANG}\n"
        for i, (pj_name, prof, bonus) in enumerate(sorted_bonuses[:n]):
            message += f"{i + 1}. {pj_name} ({prof}) {bonus:+}\n"
        message += "```"
        return await interaction.followup.send(message)

    @standard_command("Muestra los primeros n PJs con la mejor lore skill seleccionada")
    async def lore_ranking(
        self: Self,
        interaction: Interaction,
        lore_subname: str = SlashOption(
            name="lore",
            description="El lore de tu personaje (sin 'Lore ')",
            required=True,
        ),
        n: int = SlashOption(
            name="n",
            description="Cantidad de PJs a mostrar",
            required=False,
            default=5,
            min_value=1,
        ),
        group: LevelGroup = SlashOption(
            name="level_group",
            description="El grupo de nivel al que pertenecen los PJs",
            required=False,
            default=None,
            choices=LEVEL_GROUPS,
        ),
    ) -> Any:
        """Display the top n characters with the best lore skill."""
        skill = f"Lore ({lore_subname})"
        sh_skills = SkillsController()
        sh_mods = ModifiersController()
        if group is None:
            user_id = not_none(interaction.user).id
            group = get_cached_group(user_id)

        all_skills: list[SkillRow] = sh_skills.find_rows_with_values(
            {
                "Skill_name": skill,
            }
        )

        all_skills = [sk for sk in all_skills if get_cached_group(sk.Discord_id) == group]
        if not all_skills:
            return await interaction.followup.send(f"No hay PJs con la skill {skill} en el grupo {group}.")
        all_bonuses = [
            (sk.PJ_name, sk.Proficiency, sk.total_bonus(sh_mods.get_mods_row(int(sk.Discord_id))))
            for sk in all_skills
            if sk is not None and sh_mods.mods_row_exists(int(sk.Discord_id))
        ]
        sorted_bonuses = sorted(all_bonuses, key=lambda x: x[2], reverse=True)
        message: str = f"# Ranking de {skill}:\n```{CODEBLOCK_LANG}\n"
        for i, (pj_name, prof, bonus) in enumerate(sorted_bonuses[:n]):
            message += f"{i + 1}. {pj_name} ({prof}) {bonus:+}\n"
        message += "```"
        return await interaction.followup.send(message)

    @set_lore.on_autocomplete("lore_subname")
    @lore_ranking.on_autocomplete("lore_subname")
    async def autocomplete_set_lore_subname(self: Self, interaction: Interaction, lore_subname: str) -> Any:
        """Autocomplete for lore subname in set_lore command."""
        filtered_lores: list[str] = filter_lores(lore_subname, None)[:25]
        await interaction.response.send_autocomplete(filtered_lores)

    @lore.on_autocomplete("lore_subname")
    @roll_lore.on_autocomplete("lore_subname")
    async def autocomplete_lore_subname(self: Self, interaction: Interaction, lore_subname: str) -> Any:
        """Autocomplete for lore subname in lore command."""
        if interaction.user is None:
            raise ValueError("Null user")
        user_id: int = interaction.user.id

        filtered_lores: list[str] = filter_lores(lore_subname, user_id)[:25]
        await interaction.response.send_autocomplete(filtered_lores)


def skill_roll_message(user_id: int, skill_name: Skill | str, extra_mod: int = 0, extra_info: bool = False) -> str:
    """Generate a message for a skill roll."""
    mods_row = ModifiersController().get_mods_row(user_id)
    skill_row = SkillsController().get_prof_row(user_id, skill_name)

    dice = int(dndice.basic("1d20"))

    # ABILITY
    mod_type: str = skill_mod_type(skill_name)
    ability_bonus = mods_row[mod_type]

    # PROFICIENCY
    if skill_row is None:
        prof_bonus = 0
        other_bonus = 0
    else:
        prof_bonus = skill_row.prof_bonus()
        other_bonus = not_none(skill_row.Extra_bonus)

    total_mod = ability_bonus + prof_bonus + other_bonus + extra_mod
    result = dice + total_mod
    skill_msg = skill_description(ability_bonus, mod_type, skill_name, skill_row, extra_info, user_id, extra_mod)
    return (
        f"# {mods_row.PJ_name} {skill_name} roll: \n"
        f"```{CODEBLOCK_LANG}\n"
        f"{skill_msg}\n"
        f"# Resultado: {format_diceroll(dice, result)}\n"
        f"Details:[d20{total_mod:+} ({dice})]```"
    )
