"""Roles Controller Module."""

from typing import TypeVar, TypedDict

from loguru import logger
from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import JsonData, Row
from controllers.lib.utils import DataNotFoundError

ROLES_SHEET_ID = 41455486

ROLES = {
    "Healer": "⛑️",
    "Tanque": "🛡️",
    "DPS - Frontline": "⚔️",
    "DPS - Ranged": "🏹",
    "Support - Buffs": "✨",
    "Support - Debuffs": "🦠",
    "Utility": "🔧",
}


class RolesRow(Row):
    """Row for a roles entry."""

    PJ_name: str
    Discord_id: str
    Roles: JsonData[int, str]  # {index: role}

    def roles_list(self, user_id: int) -> list[str]:
        """Get the list of roles for a given user_id."""
        return list(self.Roles.values())


class RolesController(SheetsControllerBase[RolesRow]):
    """Controller for managing roles."""

    def __init__(self) -> None:
        super().__init__(ROLES_SHEET_ID, RolesRow)

    def _after_fetch(self) -> None:
        """After fetching the data, cache the list of characters that have met Caliban."""
        rows = self.get_all_rows()
        cache_roles(rows)

    def get_roles_row(self, user_id: int) -> RolesRow:
        """Get the roles row for a given user_id."""
        try:
            return self.get_row(self.find_pj_row_index(user_id))
        except (ValueError, DataNotFoundError):
            raise DataNotFoundError("Tu personaje no tiene roles definidos. Definelos con /set_roles.") from None

    def roles_row_exists(self, user_id: int) -> bool:
        """Check if the roles row exists for a given user_id."""
        try:
            r = self.get_roles_row(user_id)
            return r is not None and True
        except DataNotFoundError:
            return False


class RolesCache(TypedDict):
    """Cache for roles data."""

    Roles: list[str]


ROLES_CACHE: dict[str, RolesCache] = {}


def clear_roles_cache() -> None:
    """Clear the cached Roles."""
    global ROLES_CACHE
    ROLES_CACHE = {}
    logger.debug("Cleared Roles cache.")


def cache_roles(roles_rows: list[RolesRow]) -> None:
    """Cache the list of roles."""
    global ROLES_CACHE
    ROLES_CACHE = {
        pj.Discord_id: {
            "Roles": pj.roles_list(int(pj.Discord_id)),
        }
        for pj in roles_rows
    }
    logger.debug(f"Cached Roles data: {ROLES_CACHE}")


K = TypeVar("K")


def _get_cache(user_id: str | int, key: str, default: K) -> K:
    """Get a value from the cache."""
    global ROLES_CACHE
    user_id = str(user_id)
    if user_id not in ROLES_CACHE:
        RolesController()
    if user_id not in ROLES_CACHE:
        logger.warning(f"User ID {user_id} not found in ROLES_CACHE.")
        return default
    return ROLES_CACHE[user_id].get(key, default)


def get_cached_roles(user_id: str | int) -> list[str]:
    """Return the cached roles for a user."""
    return _get_cache(user_id, "Roles", [])


def role_emoji(role: str) -> str:
    """Return the emoji for a given role."""
    return ROLES.get(role, "❓")  # Default to a question mark if the role is not found


def pretty_roles(user_id: str | int) -> str:
    """Return a pretty string of roles for a user."""
    roles = get_cached_roles(user_id)
    if not roles:
        return "No tiene roles definidos."
    return ", ".join(f"{role_emoji(role)} {role}" for role in roles) if roles else "No tiene roles definidos."
