"""Pathfinder 2e Level Bonuses Module.

This module provides functionality to calculate proficiency bonuses based on character levels.
It defines a dictionary mapping proficiency levels to functions that compute the bonus based on the user's level.
It uses the `get_cached_level` function from the `pjs_controller` module to retrieve the user's level.
"""

from collections.abc import Callable
from PF2eData import PROF, Prof
from controllers.pjs_controller import get_cached_level


def improvised_prof_bonus(user_id: str | int) -> int:
    """Calculate the improvised proficiency bonus based on the user's level."""
    lvl = get_cached_level(user_id)
    if lvl >= 7:
        return lvl
    if lvl >= 5:
        return lvl - 1
    return lvl - 2


PROF_BONUSES: dict[Prof, Callable[[str | int], int]] = {
    PROF.Untrained: lambda x: 0,
    PROF.Improvised: improvised_prof_bonus,
    PROF.Trained: lambda x: 2 + get_cached_level(x),
    PROF.Expert: lambda x: 4 + get_cached_level(x),
    PROF.Master: lambda x: 6 + get_cached_level(x),
    PROF.Legendary: lambda x: 8 + get_cached_level(x),
}
