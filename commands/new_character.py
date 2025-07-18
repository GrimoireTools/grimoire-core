from typing import Any, Self, TypedDict

from loguru import logger
import nextcord
from nextcord import SelectOption, Interaction, SlashOption


from PF2eData import ANCESTRIES, CLASSES, HERITAGES, RELIGIONS, ARCHETYPES

from controllers.lib.cog import standard_command, Cog
from controllers.lvl_groups_controller import LEVEL_GROUPS, LevelGroup
from controllers.pjs_controller import PJsController, PJRow
from controllers.lib.utils import not_none


class PartialCharacter(TypedDict):
    Name: str
    Discord_id: str
    Player: str
    Class: str
    Ancestry: str
    Religion: str
    Level_group: LevelGroup


class HeritageDropdown(nextcord.ui.Select):
    partial_pj: PartialCharacter

    def __init__(self: Self, partial_pj: PartialCharacter) -> None:
        self.partial_pj = partial_pj
        heritages: list[str] = HERITAGES[partial_pj["Ancestry"]]

        options = [SelectOption(label=h) for h in heritages]
        options += [SelectOption(label=h, description="(Heritage versátil)") for h in HERITAGES["Versatile"]]
        super().__init__(
            placeholder="Opciones de heritage",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self: Self, interaction: Interaction) -> None:
        selected_heritage: str = self.values[0]
        try:
            assert self.view is not None
        except AssertionError:
            return
        await interaction.response.defer()
        self.view.stop()
        sh = PJsController()
        pj_dict = {
            **self.partial_pj,
            "Heritage": selected_heritage,
            "Downtime": 14,
            "Money_pp": 0,
            "Money_gp": 0,
            "Money_sp": 0,
            "Money_cp": 0,
            "Money_total": None,
            "Last_turn": "-",
            "Caliban_met": 0,
            "Languages": "Originario",
        }
        pj = PJRow.from_dict(pj_dict)
        logger.debug(f"Registering {pj}")
        row = sh.find_first_empty_row("A", strict=True)
        sh.insert_row(pj, row)
        await interaction.followup.send(f"Registrado {pj.Name}.")


class RegisterDropdownView(nextcord.ui.View):
    def __init__(self: Self, heritage_dropdown: HeritageDropdown) -> None:
        super().__init__()
        self.add_item(heritage_dropdown)


class NewCharacterCommands(Cog):

    @standard_command("Registra un nuevo personaje de Megamarch.")
    async def register(
        self: Self,
        interaction: Interaction,
        nombre_pj: str,
        nombre_jugador: str,
        clase: str = SlashOption(
            name="clase",
            description="La clase de tu personaje",
            required=True,
            choices=CLASSES,
        ),
        ascendencia: str = SlashOption(
            name="ascendencia",
            description="La ascendencia de tu personaje (escribe para el autocomplete)",
            required=True,
        ),
        religion: str = SlashOption(
            name="religión",
            description="La religión de tu personaje",
            required=True,
            choices=RELIGIONS,
        ),
        group: LevelGroup = SlashOption(
            name="level_group",
            description="El grupo de nivel al que pertenece tu personaje",
            required=True,
            choices=LEVEL_GROUPS,
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()

        if sh.character_exists(user_id):
            return await interaction.followup.send(
                "Ya tienes un personaje, muevelo al cementerio para registrar uno nuevo."
            )

        ascendencia = ascendencia.capitalize()
        if ascendencia not in ANCESTRIES:
            return await interaction.followup.send(f"'{ascendencia}' no es una ascendencia válida.")

        heritage_dropdown = HeritageDropdown(
            {
                "Name": nombre_pj,
                "Discord_id": str(user_id),
                "Player": nombre_jugador,
                "Class": clase,
                "Ancestry": ascendencia,
                "Religion": religion,
                "Level_group": group,
            }
        )

        view = RegisterDropdownView(heritage_dropdown)
        await interaction.followup.send("Selecciona un heritage para tu personaje", view=view)

    @standard_command("Registra un nuevo arquetipo para tu personaje. Si seleccionas uno que ya tienes se elimina.")
    async def register_archetype(
        self: Self,
        interaction: Interaction,
        archetype: str = SlashOption(
            name="archetype",
            description="El nuevo arquetipo de tu personaje, o uno que ya tuviera para eliminarlo.",
            required=True,
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj: PJRow = sh.get_pj_row(user_id)

        archs_list = pj.Archetypes.split(", ")
        archs_list = [arch for arch in archs_list if arch.strip()]
        if archetype in archs_list:
            archs_list.remove(archetype)
            message = f"Eliminado {archetype} de tu lista de arquetipos"
        else:
            archs_list.append(archetype)
            message = f"Añadido {archetype} a tu lista de arquetipos"

        pj.Archetypes = ", ".join(archs_list)
        sh.update_row(pj)
        await interaction.followup.send(message)

    @register.on_autocomplete("ascendencia")
    async def autocomplete_ancestry(self, interaction: Interaction, ancestry: str) -> Any:
        filtered_ancestries = []
        if ancestry:
            filtered_ancestries = [a for a in ANCESTRIES if a.lower().startswith(ancestry.lower())]
        await interaction.response.send_autocomplete(filtered_ancestries)

    @register_archetype.on_autocomplete("archetype")
    async def autocomplete_archetype(self, interaction: Interaction, archetype: str) -> Any:
        filtered_archetypes = []
        if archetype:
            filtered_archetypes = [a for a in ARCHETYPES if a.lower().startswith(archetype.lower())]
        await interaction.response.send_autocomplete(filtered_archetypes)
