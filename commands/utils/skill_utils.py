"""Utility functions for handling skills and abilities in a Discord bot context."""

import nextcord
from PF2eData import PROF, SKILL_ICONS
from controllers.saves_controller import SaveRow
from controllers.skills_controller import LoreSubnames, SkillRow
from controllers.lib.utils import not_none
from level_bonuses import PROF_BONUSES

ALTERNATE = True


def nat_20_1_message(dice_result: int) -> str:
    """Return a special message for natural 20 or 1 rolls."""
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
    """Format the skill description with the given parameters."""
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
        f"{f'{fb(prof_bonus + pj_mod_bonus + extra_bonus, True)} '.ljust(15)}"
        f"[{mod_type}: {fb(pj_mod_bonus)}]"
        f"[{f'{prof_level}:'.ljust(10)} {f'{fb(prof_bonus)}]'.rjust(15)}"
        f"{extra_msg}"
        f"{additional_msg}"
    )
    return submsg


def fb(bonus: int, bold: bool = False) -> str:
    """Format bonus numbers with colors."""
    b = 1 if bold else 0
    blue = f"\033[{b};34m"
    red = f"\033[{b};31m"
    yellow = f"\033[{b};33m"
    reset = "\033[0m"
    color = yellow if bonus == 0 else red if bonus < 0 else blue
    return f"{color}{bonus:+}{reset}"


def format_diceroll(dice: int, total: int) -> str:
    """Format a diceroll result with colors based on the value."""
    red = "\033[1;31m"
    cyan = "\033[1;36m"
    white = "\033[1;37m"
    reset = "\033[0m"
    color = red if dice == 1 else cyan if dice == 20 else white
    return f"{color}{total}{reset}"


def ability_param(ability_name: str) -> nextcord.SlashOption:
    """Create a SlashOption for an ability parameter."""
    ability_name = ability_name.lower()
    return nextcord.SlashOption(
        name=ability_name,
        description=f"El nivel de proficiencia de {ability_name.capitalize()}",
        required=True,
        choices=PROF.profs_list,
    )


def filter_lores(lore_subname: str, user_id: int | None) -> list[str]:
    """Filter lore subnames based on the provided substring and user ID."""
    if len(lore_subname) == 0:
        LoreSubnames().udpate_lore_subnames()
    lores = LoreSubnames().user_lore_subnames(user_id) if user_id else LoreSubnames().all_lore_subnames()

    return [a for a in lores if a.lower().startswith(lore_subname.lower())]
