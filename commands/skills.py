from typing import Any, Self
from nextcord import Interaction, SlashOption

import dndice
from commands.utils.skill_utils import *
from controllers.lib.cog import Cog, standard_command
from controllers.lib.utils import DataNotFoundError, not_none
from controllers.pjs_controller import PJsController
from controllers.skills_controller import SkillRow, SkillsController, skill_mod_type
from controllers.modifiers_controller import ModifiersController, ModifiersRow
from system_data import ROLL, ROLL_TYPES, SKILLS, RollType, d20

CODEBLOCK_LANG = "ansi"


class SkillCommands(Cog):

    @standard_command("Muestra la información de todas las skills de tu personaje")
    async def all_skills(self: Self, interaction: Interaction, extra_info: bool = False) -> Any:
        user_id = not_none(interaction.user).id
        mods_row = ModifiersController().get_mods_row(user_id)
        all_skill_rows = SkillsController().get_all_prof_rows(user_id)

        message: str = f"# Skills de {mods_row.PJ_name}:\n```{CODEBLOCK_LANG}\n"

        for skill_row in [sk for sk in all_skill_rows]:
            mod_type = skill_row.mod_type()
            message += skill_description(
                mods_row[mod_type],
                mod_type,
                skill_row.Skill_name,
                skill_row,
                extra_info,
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
            choices=SKILLS.keys(),
        ),
        extra_info: bool = False,
    ) -> Any:
        user_id = not_none(interaction.user).id
        mod_type = skill_mod_type(skill_name)
        mods_row = ModifiersController().get_mods_row(user_id)
        skill_row = SkillsController().get_prof_row(user_id, skill_name)

        message: str = f"## {skill_name} de {mods_row.PJ_name}:\n"
        message += f"```{CODEBLOCK_LANG}\n{skill_description(
            mods_row[mod_type],
            mod_type,
            skill_name,
            skill_row,
            extra_info,
        )}```"

        return await interaction.followup.send(message)

    @standard_command("Define la proficiencia de una skill de tu personaje")
    async def set_skill(
        self: Self,
        interaction: Interaction,
        skill: Skill = SlashOption(
            name="skill",
            description="La skill de tu personaje a definir",
            required=True,
            choices=SKILLS.keys(),
        ),
        proficiency: Prof = SlashOption(
            name="proficiency",
            description="El nivel de proficiencia de la skill",
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
        acrobatics: Prof = ability_param("acrobatics"),
        animal_handling: Prof = ability_param("animal_handling"),
        arcana: Prof = ability_param("arcana"),
        athletics: Prof = ability_param("athletics"),
        deception: Prof = ability_param("deception"),
        history: Prof = ability_param("history"),
        insight: Prof = ability_param("insight"),
        intimidation: Prof = ability_param("intimidation"),
        investigation: Prof = ability_param("investigation"),
        medicine: Prof = ability_param("medicine"),
        nature: Prof = ability_param("nature"),
        perception: Prof = ability_param("perception"),
        performance: Prof = ability_param("performance"),
        persuasion: Prof = ability_param("persuasion"),
        religion: Prof = ability_param("religion"),
        sleight_of_hand: Prof = ability_param("sleight_of_hand"),
        stealth: Prof = ability_param("stealth"),
        survival: Prof = ability_param("survival"),
    ):

        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        sh_skills = SkillsController()

        proficiencies: list[tuple[Skill, Prof]] = [
            ("Acrobatics", acrobatics),
            ("Animal Handling", animal_handling),
            ("Arcana", arcana),
            ("Athletics", athletics),
            ("Deception", deception),
            ("History", history),
            ("Insight", insight),
            ("Intimidation", intimidation),
            ("Investigation", investigation),
            ("Medicine", medicine),
            ("Nature", nature),
            ("Perception", perception),
            ("Performance", performance),
            ("Persuasion", persuasion),
            ("Religion", religion),
            ("Sleight of Hand", sleight_of_hand),
            ("Stealth", stealth),
            ("Survival", survival),
        ]

        msg = ""
        rows = []
        for skill_name, prof_value in proficiencies:
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

    @standard_command("Tira un skill check con el skill seleccionado")
    async def roll_skill(
        self: Self,
        interaction: Interaction,
        skill: Skill = SlashOption(
            name="skill",
            description="La skill de tu personaje que quieres usar",
            required=True,
            choices=[skill[0] for skill in SKILLS if skill[0] != "Lore"],
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

        message = skill_roll_message(user_id, skill, extra_modifiers, extra_info, advantage)

        return await interaction.followup.send(message)

    @standard_command("Muestra los primeros n PJs con la mejor skill seleccionada")
    async def skill_ranking(
        self: Self,
        interaction: Interaction,
        skill: str = SlashOption(
            name="skill",
            description="La skill de tu personaje que quieres usar",
            required=True,
            choices=SKILLS.keys(),
        ),
        n: int = SlashOption(
            name="n",
            description="Cantidad de PJs a mostrar",
            required=False,
            default=5,
            min_value=1,
        ),
    ) -> Any:
        sh_skills = SkillsController()
        sh_mods = ModifiersController()

        all_skills: list[SkillRow] = sh_skills.find_rows_with_values(
            {
                "Skill_name": skill,
            }
        )
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


def skill_roll_message(
    user_id: int, skill_name: Skill, extra_mod: int = 0, extra_info: bool = False, advantage: RollType = ROLL.NORMAL
) -> str:
    mods_row = ModifiersController().get_mods_row(user_id)
    skill_row = SkillsController().get_prof_row(user_id, skill_name)

    dice = d20(advantage)

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
    skill_msg = skill_description(ability_bonus, mod_type, skill_name, skill_row, extra_info, extra_mod)
    return f"# {mods_row.PJ_name} {skill_name} roll: \n```{CODEBLOCK_LANG}\n{skill_msg}\n# Resultado: {format_diceroll(dice, result)}\nDetails:[d20{total_mod:+} ({dice})]```"
