import re
from typing import Any, Self

from nextcord import slash_command, Interaction, SlashOption

from commands.utils.quotes import quotify
from controllers.lib.cog import Cog
from controllers.lib.utils import CRI_GUILD_ID, not_none, try_command
from controllers.pjs_controller import PJsController
from commands.utils.wod_utils import dots
from system_data import PREDEFINED_ABILITIES


def set_opt(name: str) -> SlashOption:
    # Discord option names must be lowercase and match a strict regex.
    option_name = re.sub(r"[^a-z0-9_]", "_", name.lower().strip())
    option_name = re.sub(r"_+", "_", option_name).strip("_")
    return SlashOption(
        option_name,
        f"New value for {name.replace('_', ' ').title()} (0-5)",
        required=True,
        autocomplete=True,
    )


class AbilitiesCommands(Cog):
    @slash_command(name="ability", guild_ids=[CRI_GUILD_ID], description="Manage character abilities")
    async def ability_group(self, interaction: Interaction) -> None:
        pass

    # ── /ability set ────────────────────────────────────────────────────────────
    @ability_group.subcommand(
        name="set", description="Sets an ability value (0-8); type any name to add a custom ability"
    )
    @try_command
    async def ability_set(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption("ability", "Ability name (predefined or custom)", required=True, autocomplete=True),
        value: int = SlashOption("value", "New value (0-8)", required=True, min_value=0, max_value=5),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        old = pj.ability(ability)
        pj.ability(ability, value)
        sh.set_row(pj)
        await interaction.followup.send(quotify(f"**{pj.Name}** — {ability}: {dots(old)} → {dots(value)}", interaction))

    @ability_group.subcommand(name="set_talents", description="Sets all talents to a value (0-5)")
    @try_command
    async def ability_set_talents(
        self: Self,
        interaction: Interaction,
        alertness: int = set_opt("Alertness"),
        art: int = set_opt("Art"),
        athletics: int = set_opt("Athletics"),
        awareness: int = set_opt("Awareness"),
        brawl: int = set_opt("Brawl"),
        dodge: int = set_opt("Dodge"),
        empathy: int = set_opt("Empathy"),
        expression: int = set_opt("Expression"),
        intimidation: int = set_opt("Intimidation"),
        intuition: int = set_opt("Intuition"),
        leadership: int = set_opt("Leadership"),
        streetwise: int = set_opt("Streetwise"),
        subterfuge: int = set_opt("Subterfuge"),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        old_values = pj.talent_abilities(all=True)
        new_values = {
            "Alertness": alertness,
            "Art": art,
            "Athletics": athletics,
            "Awareness": awareness,
            "Brawl": brawl,
            "Dodge": dodge,
            "Empathy": empathy,
            "Expression": expression,
            "Intimidation": intimidation,
            "Intuition": intuition,
            "Leadership": leadership,
            "Streetwise": streetwise,
            "Subterfuge": subterfuge,
        }
        pj.set_abilities(new_values)
        sh.set_row(pj)
        changes = "\n".join(
            f"  {ability:<14} {dots(old_values[ability])} → {dots(new_values[ability])}" for ability in new_values
        )
        await interaction.followup.send(quotify(f"**{pj.Name}** — Talents updated:\n```\n{changes}\n```", interaction))

    @ability_group.subcommand(name="set_skills", description="Sets all skills to a value (0-5)")
    @try_command
    async def ability_set_skills(
        self: Self,
        interaction: Interaction,
        animal_ken: int = set_opt("Animal_Ken"),
        crafts: int = set_opt("Crafts"),
        demolitions: int = set_opt("Demolitions"),
        drive: int = set_opt("Drive"),
        etiquette: int = set_opt("Etiquette"),
        firearms: int = set_opt("Firearms"),
        larceny: int = set_opt("Larceny"),
        martial_arts: int = set_opt("Martial_Arts"),
        meditation: int = set_opt("Meditation"),
        melee: int = set_opt("Melee"),
        performance: int = set_opt("Performance"),
        research_sk: int = set_opt("Research_Sk"),
        security: int = set_opt("Security"),
        stealth: int = set_opt("Stealth"),
        survival: int = set_opt("Survival"),
        technology_sk: int = set_opt("Technology_Sk"),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        old_values = pj.skill_abilities(all=True)
        new_values = {
            "Animal_Ken": animal_ken,
            "Crafts": crafts,
            "Demolitions": demolitions,
            "Drive": drive,
            "Etiquette": etiquette,
            "Firearms": firearms,
            "Larceny": larceny,
            "Martial_Arts": martial_arts,
            "Meditation": meditation,
            "Melee": melee,
            "Performance": performance,
            "Research_Sk": research_sk,
            "Security": security,
            "Stealth": stealth,
            "Survival": survival,
            "Technology_Sk": technology_sk,
        }
        pj.set_abilities(new_values)
        sh.set_row(pj)
        changes = "\n".join(
            f"  {ability:<14} {dots(old_values[ability])} → {dots(new_values[ability])}" for ability in new_values
        )
        await interaction.followup.send(quotify(f"**{pj.Name}** — Skills updated:\n```\n{changes}\n```", interaction))

    @ability_group.subcommand(name="set_knowledges", description="Sets all knowledges to a value (0-5)")
    @try_command
    async def ability_set_knowledges(
        self: Self,
        interaction: Interaction,
        academics: int = set_opt("Academics"),
        bureaucracy: int = set_opt("Bureaucracy"),
        computer: int = set_opt("Computer"),
        cosmology: int = set_opt("Cosmology"),
        enigmas: int = set_opt("Enigmas"),
        esoterica: int = set_opt("Esoterica"),
        finance: int = set_opt("Finance"),
        investigation: int = set_opt("Investigation"),
        law: int = set_opt("Law"),
        linguistics: int = set_opt("Linguistics"),
        medicine: int = set_opt("Medicine"),
        occult: int = set_opt("Occult"),
        politics: int = set_opt("Politics"),
        research_kn: int = set_opt("Research_Kn"),
        science: int = set_opt("Science"),
        technology_kn: int = set_opt("Technology_Kn"),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        old_values = pj.knowledge_abilities(all=True)
        new_values = {
            "Academics": academics,
            "Bureaucracy": bureaucracy,
            "Computer": computer,
            "Cosmology": cosmology,
            "Enigmas": enigmas,
            "Esoterica": esoterica,
            "Finance": finance,
            "Investigation": investigation,
            "Law": law,
            "Linguistics": linguistics,
            "Medicine": medicine,
            "Occult": occult,
            "Politics": politics,
            "Research_Kn": research_kn,
            "Science": science,
            "Technology_Kn": technology_kn,
        }
        pj.set_abilities(new_values)
        sh.set_row(pj)
        changes = "\n".join(
            f"  {ability:<14} {dots(old_values[ability])} → {dots(new_values[ability])}" for ability in new_values
        )
        await interaction.followup.send(
            quotify(f"**{pj.Name}** — Knowledges updated:\n```\n{changes}\n```", interaction)
        )

    # ── /ability view ───────────────────────────────────────────────────────────

    @ability_group.subcommand(name="view", description="Shows an ability value and specialty if any")
    @try_command
    async def ability_view(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption("ability", "Ability name", required=True, autocomplete=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        value = pj.ability(ability)
        spec = pj.specialty(ability)
        spec_str = f"  *(specialty: {spec})*" if spec else ""
        await interaction.followup.send(quotify(f"**{pj.Name}** — {ability}: {dots(value)}{spec_str}", interaction))

    @ability_group.subcommand(name="all", description="Shows all the abilities and their values, including specialties")
    @try_command
    async def ability_all(
        self: Self,
        interaction: Interaction,
        all: bool = SlashOption("all", "Show all abilities including ones at 0", required=False, default=False),
    ) -> Any:
        user_id = not_none(interaction.user).id
        pj = PJsController().get_pj_row(user_id)
        knowledges = pj.knowledge_abilities(all)
        skills = pj.skill_abilities(all)
        talents = pj.talent_abilities(all)
        customs = pj.custom_abilities()

        lines = (
            "Talents:\n"
            + "\n".join(
                f"  {k:<14} {dots(v)} ({v}) {f'[{pj.Specialties[k]}]' if k in pj.Specialties else ''}"
                for k, v in talents.items()
            )
            + "\n\n"
            if talents
            else ""
        )
        lines += (
            "Skills:\n"
            + "\n".join(
                f"  {k:<14} {dots(v)} ({v}) {f'[{pj.Specialties[k]}]' if k in pj.Specialties else ''}"
                for k, v in skills.items()
            )
            + "\n\n"
            if skills
            else ""
        )
        lines += (
            "Knowledges:\n"
            + "\n".join(
                f"  {k:<14} {dots(v)} ({v}) {f'[{pj.Specialties[k]}]' if k in pj.Specialties else ''}"
                for k, v in knowledges.items()
            )
            + "\n\n"
            if knowledges
            else ""
        )

        lines += (
            "Custom Abilities:\n"
            + "\n".join(
                f"  {k:<14} {dots(v)} ({v}) {f'[{pj.Specialties[k]}]' if k in pj.Specialties else ''}"
                for k, v in customs.items()
            )
            if customs
            else ""
        )
        await interaction.followup.send(quotify(f"**{pj.Name}** — Abilities:\n```\n{lines}\n```", interaction))

    # ── /specialty set ────────────────────────────────────────────────────────
    @slash_command(name="specialty", guild_ids=[CRI_GUILD_ID], description="Manage ability specialties")
    async def specialty_group(self, interaction: Interaction) -> None:
        pass

    @specialty_group.subcommand(name="set", description="Adds or replaces a specialty for an ability")
    @try_command
    async def specialty_set(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption(
            "ability", "Ability or Attribute to specialise in", required=True, autocomplete=True
        ),
        description: str = SlashOption("description", "Specialty description (e.g. 'Haymaker')", required=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        pj.specialty(ability, description)
        sh.set_row(pj)
        await interaction.followup.send(
            quotify(
                f"**{pj.Name}** — {ability} specialty set to **{description}**. "
                f"10s will count as 2 successes when rolling this ability.",
                interaction,
            )
        )

    @specialty_group.subcommand(name="remove", description="Removes the specialty from an ability")
    @try_command
    async def specialty_remove(
        self: Self,
        interaction: Interaction,
        ability: str = SlashOption("ability", "Ability to remove specialty from", required=True, autocomplete=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj = sh.get_pj_row(user_id)
        if ability not in pj.Specialties:
            return await interaction.followup.send(quotify(f"**{ability}** has no specialty.", interaction))
        del pj.Specialties[ability]
        sh.set_row(pj)
        await interaction.followup.send(quotify(f"**{pj.Name}** — specialty for **{ability}** removed.", interaction))

    # ── Autocomplete ──────────────────────────────────────────────────────────

    @ability_set.on_autocomplete("ability")
    async def _ac_ability_set(self, interaction: Interaction, query: str) -> None:
        await self._ability_autocomplete(interaction, query, include_custom=True)

    @ability_view.on_autocomplete("ability")
    async def _ac_ability_view(self, interaction: Interaction, query: str) -> None:
        await self._ability_autocomplete(interaction, query, include_custom=True)

    @specialty_set.on_autocomplete("ability")
    async def _ac_specialty_set(self, interaction: Interaction, query: str) -> None:
        # Only abilities the character actually has a value in
        await self._ability_or_attribute_autocomplete(interaction, query, only_known=True)

    @specialty_remove.on_autocomplete("ability")
    async def _ac_specialty_remove(self, interaction: Interaction, query: str) -> None:
        # Only abilities that already have a specialty
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            names = list(pj.Specialties.keys())
        except Exception:
            names = []
        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])

    async def _ability_autocomplete(
        self,
        interaction: Interaction,
        query: str,
        include_custom: bool = False,
        only_known: bool = False,
    ) -> None:
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            known = list(pj.Abilities.keys())
        except Exception:
            known = []
            pj = None

        if only_known:
            names = known
        elif include_custom:
            # Predefined first, then any custom skills the character already has
            custom = [s for s in known if s not in PREDEFINED_ABILITIES]
            names = PREDEFINED_ABILITIES + custom
        else:
            names = PREDEFINED_ABILITIES

        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])

    async def _ability_or_attribute_autocomplete(
        self,
        interaction: Interaction,
        query: str,
        include_custom: bool = False,
        only_known: bool = False,
    ) -> None:
        try:
            user_id = not_none(interaction.user).id
            pj = PJsController.cached().get_pj_row(user_id)
            known = list(pj.Abilities.keys()) + list(pj.Attributes.keys())
        except Exception:
            known = []
            pj = None

        if only_known:
            names = known
        elif include_custom:
            # Predefined first, then any custom skills or attributes the character already has
            custom = [s for s in known if s not in PREDEFINED_ABILITIES]
            names = PREDEFINED_ABILITIES + custom
        else:
            names = PREDEFINED_ABILITIES

        if query:
            names = [s for s in names if s.lower().startswith(query.lower())]
        await interaction.response.send_autocomplete(names[:25])
