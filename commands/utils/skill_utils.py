import nextcord
from PF2eData import PROF, SKILL_ICONS
from controllers.saves_controller import SaveRow
from controllers.skills_controller import LoreSubnames, SkillRow
from controllers.lib.utils import not_none
from level_bonuses import PROF_BONUSES

ALTERNATE = True


def nat_20_1_message(dice_result: int) -> str:
    if dice_result == 20:
        return "**Nat 20!** "
    elif dice_result == 1:
        return "**Nat 1!** "
    else:
        return ""


def skill_description(
    pj_mod_bonus: int,
    mod_type: str,
    skill_name: str,
    pj_skill: None | SkillRow | SaveRow,
    extra_info: bool,
    user_id: str | int,
    additional_mod: int = 0,
) -> str:
    global ALTERNATE
    ALTERNATE = not ALTERNATE
    just_char = "·" if ALTERNATE else " "
    just_spacing = 20

    if pj_skill is None:
        prof_level = PROF.Untrained
        skill_title = f"{skill_name}? "
        extra_msg = ""
        extra_bonus = 0
        extra_descripcion = ""
    else:
        skill_title = f"{skill_name} "
        prof_level: str = pj_skill.Proficiency
        extra_bonus: int = not_none(pj_skill.Extra_bonus)
        extra_descripcion: str = pj_skill.Bonus_description

        extra_msg = (
            ""
            if (extra_bonus == 0 and extra_descripcion == "")
            else f"[Other: {fb(extra_bonus)}{f' ({extra_descripcion})' if extra_info else ''}]"
        )
    additional_msg = f"[Extra: {fb(additional_mod)}]" if additional_mod != 0 else ""
    prof_bonus: int = PROF_BONUSES[prof_level](user_id)
    submsg: str = (
        f"\n{PROF.ICONS[prof_level]} {SKILL_ICONS[skill_name]} {skill_title.ljust(just_spacing, just_char)} "
        f'{f"{fb(prof_bonus + pj_mod_bonus + extra_bonus, True)} ".ljust(15)}'
        f"[{mod_type}: {fb(pj_mod_bonus)}]"
        f"[{f'{prof_level}:'.ljust(10)} {f'{fb(prof_bonus)}]'.rjust(15)}"
        f"{extra_msg}"
        f"{additional_msg}"
    )
    return submsg


def fb(bonus: int, bold: bool = False) -> str:
    """Format bonus numbers with colors."""
    b = 1 if bold else 0
    BLUE = f"\033[{b};34m"
    RED = f"\033[{b};31m"
    YELLOW = f"\033[{b};33m"
    RESET = "\033[0m"
    color = YELLOW if bonus == 0 else RED if bonus < 0 else BLUE
    return f"{color}{bonus:+}{RESET}"


def format_diceroll(dice: int, total: int) -> str:
    RED = "\033[1;31m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"
    RESET = "\033[0m"
    color = RED if dice == 1 else CYAN if dice == 20 else WHITE
    return f"{color}{total}{RESET}"


def ability_param(ability_name: str):
    ability_name = ability_name.lower()
    return nextcord.SlashOption(
        name=ability_name,
        description=f"El nivel de proficiencia de {ability_name.capitalize()}",
        required=True,
        choices=PROF.profs_list,
    )


def filter_lores(lore_subname: str, user_id: int | None) -> list[str]:
    if len(lore_subname) == 0:
        LoreSubnames().udpate_lore_subnames()
    lores = LoreSubnames().user_lore_subnames(user_id) if user_id else LoreSubnames().all_lore_subnames()

    return [a for a in lores if a.lower().startswith(lore_subname.lower())]
