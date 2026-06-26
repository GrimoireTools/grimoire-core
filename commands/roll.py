from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController
from commands.utils.wod_roll_utils import wod_roll, format_roll
from system_data import ATTRIBUTES, PREDEFINED_ABILITIES, Ability, Attribute


class RollCommands(Cog):

    # ── /roll ─────────────────────────────────────────────────────────────────
    @slash_command(name="roll", guild_ids=[CRI_GUILD_ID], description="Roll an attribute + ability dice pool")
    @try_command
    async def roll(
        self: Self,
        interaction: Interaction,
        attribute: Attribute = SlashOption(
            "attribute", "Attribute to roll with",
            required=True, choices=ATTRIBUTES,
        ),
        ability: Ability = SlashOption(
            "ability", "Ability to roll with (optional)",
            required=False, default=None, autocomplete=True,
        ),
        apply_specialty: bool = SlashOption(
            "specialty", "Apply specialty (10s = 2 successes)",
            required=False, default=False,
        ),
        modifier: int = SlashOption(
            "modifier", "Extra dice to add (negative to remove)",
            required=False, default=0,
        ),
        difficulty: int = SlashOption(
            "difficulty", "Target number for a success (default 6)",
            required=False, default=6, min_value=2, max_value=10,
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController.cached().get_pj_row(user_id)

        attr_val = pj.attribute(attribute)
        ability_val = pj.ability(ability) if ability else 0
        has_specialty = bool(ability and pj.specialty(
            ability)) and apply_specialty
        pool = attr_val + ability_val + modifier

        result = wod_roll(pool, difficulty, has_specialty)

        # Build label line
        parts = [f"**{attribute}** {attr_val}"]
        if ability:
            spec = pj.specialty(ability)
            spec_tag = f" *({spec})*" if spec and apply_specialty else ""
            parts.append(f"**{ability}** {ability_val}{spec_tag}")
        if modifier:
            parts.append(f"modifier {modifier:+}")
        label = " + ".join(parts) + \
            f"  |  pool **{pool}**  diff **{difficulty}**"

        await interaction.followup.send(
            f"{label}\n```ansi\n{format_roll(result)}\n```"
        )

    # ── /roll_pool ────────────────────────────────────────────────────────────
    @slash_command(name="roll_pool", guild_ids=[CRI_GUILD_ID], description="Roll a raw dice pool (no character lookup)")
    @try_command
    async def roll_pool(
        self: Self,
        interaction: Interaction,
        pool: int = SlashOption(
            "pool", "Number of dice to roll", required=True, min_value=0),
        difficulty: int = SlashOption(
            "difficulty", "Target number for a success (default 6)",
            required=False, default=6, min_value=2, max_value=10,
        ),
        specialty: bool = SlashOption(
            "specialty", "Apply specialty (10s = 2 successes)",
            required=False, default=False,
        ),
    ) -> Any:
        result = wod_roll(pool, difficulty, specialty)
        label = f"pool **{pool}**  diff **{difficulty}**"
        await interaction.followup.send(
            f"{label}\n```ansi\n{format_roll(result)}\n```"
        )

    # ── Autocomplete ──────────────────────────────────────────────────────────

    @roll.on_autocomplete("ability")
    async def _ac_roll_ability(self, interaction: Interaction, query: str):
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            names = list(pj.Abilities.keys()) + ["No Ability"]
        except Exception:
            names = PREDEFINED_ABILITIES + ["No Ability"]
        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])
