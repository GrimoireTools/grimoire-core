from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from commands.utils.quotes import quotify
from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController
from commands.utils.wod_roll_utils import wod_roll, format_roll
from system_data import ATTRIBUTES, PREDEFINED_ABILITIES, Ability, Attribute


class RollCommands(Cog):
    # ── /roll ─────────────────────────────────────────────────────────────────
    @slash_command(
        name="roll",
        guild_ids=[CRI_GUILD_ID],
        description="Roll an attribute + ability dice pool",
    )
    @try_command
    async def roll(
        self: Self,
        interaction: Interaction,
        attribute: Attribute = SlashOption(
            "attribute",
            "Attribute to roll with",
            required=False,
            default=None,
            choices=ATTRIBUTES,
        ),
        ability: Ability = SlashOption(
            "ability",
            "Ability to roll with (optional)",
            required=False,
            default="",
            autocomplete=True,
        ),
        apply_specialty: bool = SlashOption(
            "specialty",
            "Apply specialty (10s = 2 successes)",
            required=False,
            default=False,
        ),
        modifier: int = SlashOption(
            "modifier",
            "Extra dice to add (negative to remove)",
            required=False,
            default=0,
        ),
        difficulty: int = SlashOption(
            "difficulty",
            "Target number for a success (default 6)",
            required=False,
            default=6,
            min_value=2,
            max_value=10,
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController.cached().get_pj_row(user_id)

        attr_val = pj.attribute(attribute) if attribute else 0
        ability_val = pj.ability(ability) if ability else 0
        attr_spec = bool(attribute and pj.specialty(attribute))
        ability_spec = bool(ability and pj.specialty(ability))
        has_specialty = attr_spec or ability_spec

        pool = attr_val + ability_val + modifier

        result = wod_roll(pool, difficulty, has_specialty and apply_specialty)

        # Build label line
        parts = []
        if attribute:
            parts.append(f"**{attribute}** {attr_val}")
            if attr_spec and apply_specialty:
                parts[-1] += f" [{pj.specialty(attribute)}]"
        if ability:
            parts.append(f"**{ability}** {ability_val}")
            if ability_spec and apply_specialty:
                parts[-1] += f" [{pj.specialty(ability)}]"

        if modifier:
            parts.append(f"modifier {modifier:+}")
        label = " + ".join(parts) + f"  |  pool **{pool}**  diff **{difficulty}**"
        if apply_specialty and not has_specialty:
            label += "  |  specialty ignored (no specialty found)"
        elif apply_specialty and has_specialty:
            label += "  |  specialty applied"

        if result.successes > 0:
            await interaction.followup.send(
                quotify(f"{label}\n```ansi\n{format_roll(result)}\n```", interaction, "success")
            )
        elif result.is_botch:
            await interaction.followup.send(
                quotify(f"{label}\n```ansi\n{format_roll(result)}\n```", interaction, "botch", 34)
            )
        else:
            await interaction.followup.send(
                quotify(f"{label}\n```ansi\n{format_roll(result)}\n```", interaction, "failure")
            )

    # ── /roll_pool ────────────────────────────────────────────────────────────
    @slash_command(
        name="roll_pool",
        guild_ids=[CRI_GUILD_ID],
        description="Roll a raw dice pool (no character lookup)",
    )
    @try_command
    async def roll_pool(
        self: Self,
        interaction: Interaction,
        pool: int = SlashOption("pool", "Number of dice to roll", required=True, min_value=0),
        difficulty: int = SlashOption(
            "difficulty",
            "Target number for a success (default 6)",
            required=False,
            default=6,
            min_value=2,
            max_value=10,
        ),
        specialty: bool = SlashOption(
            "specialty",
            "Apply specialty (10s = 2 successes)",
            required=False,
            default=False,
        ),
    ) -> Any:
        result = wod_roll(pool, difficulty, specialty)
        label = f"pool **{pool}**  diff **{difficulty}**"
        if result.successes > 0:
            await interaction.followup.send(
                quotify(f"{label}\n```ansi\n{format_roll(result)}\n```", interaction, "success")
            )
        elif result.is_botch:
            await interaction.followup.send(
                quotify(f"{label}\n```ansi\n{format_roll(result)}\n```", interaction, "botch", 34)
            )
        else:
            await interaction.followup.send(
                quotify(f"{label}\n```ansi\n{format_roll(result)}\n```", interaction, "failure")
            )

    # ── Autocomplete ──────────────────────────────────────────────────────────

    @roll.on_autocomplete("ability")
    async def _ac_roll_ability(self, interaction: Interaction, query: str) -> None:
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            names = [*list(pj.Abilities.keys()), "No Ability"]
        except Exception:
            names = [*PREDEFINED_ABILITIES, "No Ability"]
        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])
