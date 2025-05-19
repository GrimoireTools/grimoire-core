from loguru import logger
from commands.utils.skill_utils import filter_lores
from controllers.lib.cog import standard_command, Cog
from typing import Any, Self

import dndice
from nextcord import Interaction, SlashOption


from PF2eData import EARN_INCOME, LORELESS_SKILLS, PROF
import random

from controllers.lib.utils import not_none, check_results, result_name
from controllers.modifiers_controller import ModifiersController, ModifiersRow
from controllers.pjs_controller import PJRow, PJsController
from controllers.skills_controller import SkillRow, SkillsController
from controllers.salary_controller import get_level_global


class EarnIncomeCommands(Cog):
    # =====================================================================================================================

    @standard_command("Calcula las ganancias de Earn Income.")
    async def earn_income_manual(
        self: Self,
        interaction: Interaction,
        taskLevel: int = SlashOption("task-level", "Nivel del trabajo", True, min_value=0, max_value=21),
        profLevel: str = SlashOption(
            "proficiency-level",
            "Nivel de proficiencia de la skill usada",
            True,
            choices=["Trained", "Expert", "Master", "Legendary"],
        ),
        downtimeUsed: int = SlashOption(
            "downtime-used",
            "Dias de downtime usados en trabajar",
            True,
            min_value=7,
            default=7,
        ),
        checkBonus: int = SlashOption("check-bonus", "Bono al check utilizado", True),
        dcChange: int = SlashOption(
            "dc-adjustment",
            "Cambios al DC impuestos por el DM. +3 para habilidades que no sean Performance, Crafting o Lore.",
            False,
            default=0,
        ),
    ) -> Any:
        dice = int(dndice.basic("1d20"))
        check_value = dice + checkBonus
        DC = EARN_INCOME[taskLevel][0] + dcChange
        check_result = check_results(DC, check_value, dice)

        income, final_dt_usage = calc_job_income_and_dt(taskLevel, downtimeUsed, check_result, profLevel)

        message = f"""Con un {check_value} ({dice}+{checkBonus}) vs DC {DC} (lvl {taskLevel}), obtienes un {result_name(check_result)}.
    Trabajas {final_dt_usage} dias y obtienes {income:.2f} gp al día, por un total de {income * final_dt_usage:.2f} gp.
    (debes updatearlos manualmente)
    """  # noqa: E501
        await interaction.followup.send(message)

    # =====================================================================================================================

    @standard_command("Calcula y genera las ganancias de Earn Income. El DC se calcula solo.")
    async def earn_income(
        self: Self,
        interaction: Interaction,
        taskLevel: int = SlashOption("task-level", "Nivel del trabajo", True, min_value=0, max_value=21),
        skill_name: str = SlashOption(
            "skill",
            "Skill utilizada. Trained Only.",
            True,
            choices=[sk_name for sk_name in LORELESS_SKILLS],
        ),
        downtime_used: int = SlashOption(
            "downtime-used",
            "Dias de downtime usados en trabajar",
            True,
            min_value=7,
            default=7,
        ),
        additional_bonus: int = SlashOption(
            "additional-check-bonus", "Bonos adicionales al check utilizado", False, default=0
        ),
        dc_change: int = SlashOption("dc-adjustment", "Cambios al DC impuestos por el DM.", False, default=0),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh_pjs = PJsController()
        pj = sh_pjs.get_pj_row(user_id)
        pj_dt = not_none(pj.Downtime)
        if pj_dt - downtime_used < 0:
            return await interaction.followup.send("No tienes suficiente downtime para esta transacción")

        sh_mods = ModifiersController()
        mods = sh_mods.get_mods_row(user_id)
        sh_skills = SkillsController()
        skill: SkillRow = sh_skills.get_skill_or_untrained(user_id, skill_name)

        if skill.Proficiency in [PROF.Untrained, PROF.Improvised]:
            not_defined = " No has definido esta skill con /set_skill." if skill.PJ_name == "Anonymous" else ""
            return await interaction.followup.send(f"No puedes hacer Earn Income con una skill Untrained.{not_defined}")

        harder_dc = skill_name not in ["Crafting", "Performance"]
        harder_dc_adjustment = 3 if harder_dc else 0
        DC = EARN_INCOME[taskLevel][0] + dc_change + harder_dc_adjustment

        dice = int(dndice.basic("1d20"))
        check_value = dice + skill.total_bonus(mods, additional_bonus)
        check_result = check_results(DC, check_value, dice)

        income, final_dt_usage = calc_job_income_and_dt(taskLevel, downtime_used, check_result, skill.Proficiency)

        new_dt_total = pj_dt - final_dt_usage
        pj.Downtime = new_dt_total
        old_money = pj.calc_money()
        pj.update_money(old_money + income * final_dt_usage)

        sh_pjs.set_row(pj)
        await interaction.followup.send(
            income_message(
                taskLevel,
                skill,
                pj,
                mods,
                additional_bonus,
                pj_dt,
                old_money,
                harder_dc,
                DC,
                dice,
                income,
            )
        )

    @standard_command("Calcula y genera las ganancias de Earn Income con un Lore. El DC se calcula solo.")
    async def earn_income_lore(
        self: Self,
        interaction: Interaction,
        taskLevel: int = SlashOption("task-level", "Nivel del trabajo", True, min_value=0, max_value=21),
        lore: str = SlashOption(
            "lore",
            "El lore de tu personaje (sin 'Lore '). Trained Only.",
            True,
        ),
        downtime_used: int = SlashOption(
            "downtime-used",
            "Dias de downtime usados en trabajar",
            True,
            min_value=7,
            default=7,
        ),
        additional_bonus: int = SlashOption(
            "additional-check-bonus", "Bonos adicionales al check utilizado", False, default=0
        ),
        dc_change: int = SlashOption("dc-adjustment", "Cambios al DC impuestos por el DM.", False, default=0),
        experienced_prof: bool = SlashOption(
            "experienced-professional", "Aplicar Experienced Professional.", False, default=False
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh_pjs = PJsController()
        pj = sh_pjs.get_pj_row(user_id)
        pj_dt = not_none(pj.Downtime)

        if pj_dt - downtime_used < 0:
            return await interaction.followup.send("No tienes suficiente downtime para esta transacción")

        sh_mods = ModifiersController()
        mods = sh_mods.get_mods_row(user_id)
        sh_skills = SkillsController()
        skill_name = f"Lore ({lore})"
        skill: SkillRow = sh_skills.get_skill_or_untrained(user_id, skill_name)

        if skill.Proficiency in [PROF.Untrained, PROF.Improvised]:
            not_defined = " No has definido esta skill con /set_skill." if skill.PJ_name == "Anonymous" else ""
            return await interaction.followup.send(f"No puedes hacer Earn Income con una skill Untrained.{not_defined}")

        DC = EARN_INCOME[taskLevel][0] + dc_change

        dice = int(dndice.basic("1d20"))
        check_value = dice + skill.total_bonus(mods, additional_bonus)
        check_result = check_results(DC, check_value, dice)

        income, final_dt_usage = calc_job_income_and_dt(taskLevel, downtime_used, check_result, skill.Proficiency)
        if experienced_prof:  # https://2e.aonprd.com/Feats.aspx?ID=5144
            if check_result == 1 and skill.Proficiency != PROF.Trained:
                # Expert+: Double the income for a failure if it was not originally crit failure
                income *= 2
            if check_result == 0:
                # Crit failure -> failure
                check_result = 1

        new_dt_total = pj_dt - final_dt_usage
        pj.Downtime = new_dt_total
        old_money = pj.calc_money()
        pj.update_money(old_money + income * final_dt_usage)

        sh_pjs.set_row(pj)
        await interaction.followup.send(
            income_message(
                taskLevel,
                skill,
                pj,
                mods,
                additional_bonus,
                pj_dt,
                old_money,
                False,
                DC,
                dice,
                income,
            )
        )

    @standard_command("Genera trabajos especiales.")
    async def gen_jobs(
        self: Self,
        interaction: Interaction,
        taskLevel: int = SlashOption(
            "task-level", "Nivel base de los trabajos", False, min_value=0, max_value=21, default=None
        ),
        tasksAmt: int = SlashOption(
            "tasks-amount", "Cantidad de trabajos", False, min_value=0, max_value=10, default=4
        ),
    ) -> Any:
        taskLevel = taskLevel if taskLevel is not None else get_level_global()
        message = (
            "# Trabajos mensuales\n"
            "Todos los trabajos duran 14 dias y se pueden hacer 1 sola vez por PJ.\n"
            "Como recordatorio, todos los trabajos con skills que no sean Crafting, Performance o Lore tienen un +3 al DC\n\n"
        )
        chosen_skills = random.sample(LORELESS_SKILLS, tasksAmt)
        job_messages = [job_message(sk, taskLevel) for sk in chosen_skills]
        message += "\n".join(job_messages)

        await interaction.followup.send(message)

    @earn_income_lore.on_autocomplete("lore")
    async def autocomplete_lore_subname(self: Self, interaction: Interaction, lore_subname: str) -> Any:
        user_id = not_none(interaction.user).id

        filtered_lores: list[str] = filter_lores(lore_subname, user_id)
        await interaction.response.send_autocomplete(filtered_lores)


def job_message(skill: str, base_lvl: int) -> str:
    """"""
    lvl = min(21, base_lvl + random.choices([0, 1, 2], [0.6, 0.3, 0.1])[0])
    if skill_is_standard(skill):
        dc_adjustment = random.choice([-0, -1, -2])
        dc_message = f"{dc_adjustment:+} al DC"
        extra_dc = 0

    else:
        dc_adjustment = random.choice([-1, -2, -3])
        dc_message = f"{dc_adjustment:+} al DC (+3 por skill no estandar)"
        extra_dc = 3

    dc = EARN_INCOME[lvl][0] + dc_adjustment + extra_dc

    return (
        f"### Trabajo de **{skill}**:\n"
        f"Trabajo de Nivel {lvl}. {dc_message} (DC total {dc})"
        f"```/earn_income task-level:{lvl} skill:{skill} downtime-used:14 dc-adjustment:{dc_adjustment}```"
    )


def calc_job_income_and_dt(taskLevel: int, downtimeUsed: int, check_result: int, prof: str) -> tuple[float, int]:
    prof_column = ["Trained", "Expert", "Master", "Legendary"].index(prof) + 1

    if check_result == 0:
        # crit failure
        income = 0
        final_dt_usage = 7
    if check_result == 1:
        # failure
        income = EARN_INCOME[taskLevel][1][0]
        final_dt_usage = 7
    if check_result == 2:
        # success
        income = EARN_INCOME[taskLevel][1][prof_column]
        final_dt_usage = downtimeUsed
    if check_result == 3:
        # Critical success
        income = EARN_INCOME[taskLevel + 1][1][prof_column]
        final_dt_usage = downtimeUsed
    return income, final_dt_usage


def skill_is_standard(skill: str) -> bool:
    return skill == "Performance" or skill == "Crafting" or skill.startswith("Lore")


def income_message(
    taskLevel: int,
    skill: SkillRow,
    pj: PJRow,
    mods: ModifiersRow,
    extra_bonus: int,
    old_dt: int,
    old_money: float,
    harder_dc: bool,
    DC: int,
    dice: int,
    income: float,
):

    skill_name = skill.Skill_name
    skill_msg = skill.modifiers_description(mods, extra_bonus)
    bonus = skill.total_bonus(mods, extra_bonus)
    check_result = check_results(DC, dice + bonus, dice)
    harder_dc_message = f" (con +3 al DC por usar {skill_name})" if harder_dc else ""
    new_dt = not_none(pj.Downtime)
    final_dt_usage = old_dt - new_dt
    crit_fail_message = (
        "" if check_result != 0 else "\nDebido a tu crit failure, tu proximo trabajo tiene un -1 al nivel."
    )

    return f"""## {pj.Name}: Earn income de {skill_name} lvl {taskLevel}
Con un {dice + bonus} ({dice}{bonus:+} {skill_msg}) vs DC {DC}{harder_dc_message}, obtienes un {result_name(check_result)}.
    Trabajas {final_dt_usage} dias y obtienes {income:.2f} gp al día, por un total de {income * final_dt_usage:.2f} gp.
    Cambio de DT: {old_dt} -> {new_dt:.2f}
    Cambio de Dinero: {old_money:.2f} -> {pj.calc_money():.2f}{crit_fail_message}
    """
