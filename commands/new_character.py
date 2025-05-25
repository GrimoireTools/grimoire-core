from typing import Any, Self

import nextcord
from nextcord import SelectOption, Interaction, SlashOption


from system_data import ALIGNMENTS, CLASSES, GODS, RACES, Class

from controllers.lib.cog import standard_command, Cog
from controllers.pjs_controller import PJsController, PJRow
from controllers.lib.utils import not_none

SUBCLASSES: list[str] = []
for cls, subs in CLASSES.items():
    for sub in subs:
        SUBCLASSES.append(f"{cls} - {sub}")


class SubraceDropdown(nextcord.ui.Select):

    partial_pj: dict[str, Any]

    def __init__(self: Self, partial_pj: dict[str, Any]) -> None:
        self.partial_pj = partial_pj
        subrace: list[str] = RACES[partial_pj["Race"]]

        super().__init__(
            placeholder="Opciones de heritage",
            min_values=1,
            max_values=1,
            options=[SelectOption(label=h) for h in subrace],
        )

    async def callback(self: Self, interaction: Interaction) -> None:
        selected_subrace: str = self.values[0]
        try:
            assert self.view is not None
        except AssertionError:
            return
        await interaction.response.defer()
        self.view.stop()
        sh = PJsController()
        self.partial_pj["Subrace"] = selected_subrace
        pj = PJRow.from_dict(self.partial_pj)
        sh.insert_row(pj, sh.find_first_empty_row("A", strict=True))
        return await interaction.followup.send(
            f"Registrado {pj.Name}.\nUtiliza `/set_ability_scores` para definir los Ability Scores de tu personaje,"
            f" `/set_all_skills` para definir tus skills y `set_all_saves` para definir tus saves."
        )


class RegisterDropdownView(nextcord.ui.View):
    def __init__(self: Self, heritage_dropdown: SubraceDropdown) -> None:
        super().__init__()
        self.add_item(heritage_dropdown)


class NewCharacterCommands(Cog):

    @standard_command("Registra un nuevo personaje de Dungeonmarch.")
    async def register(
        self: Self,
        interaction: Interaction,
        nombre_pj: str,
        nombre_jugador: str,
        clase: Class = SlashOption(
            name="clase",
            description="La clase de tu personaje",
            required=True,
            choices=CLASSES.keys(),
        ),
        race: str = SlashOption(
            name="raza",
            description="La ascendencia de tu personaje (escribe para el autocomplete)",
            required=True,
        ),
        deity: str = SlashOption(
            name="deidad",
            description="La religión de tu personaje",
            required=True,
            choices=GODS,
        ),
        alignment: str = SlashOption(
            name="alineamiento", description="El alineamiento de tu personaje", required=True, choices=ALIGNMENTS
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()

        if sh.character_exists(user_id):
            return await interaction.followup.send(
                "Ya tienes un personaje, muevelo al cementerio para registrar uno nuevo."
            )

        if race not in RACES:
            return await interaction.followup.send(f"'{race}' no es una raza válida.")

        partial_pj = PJRow.partial_create(
            name=nombre_pj,
            discord_id=user_id,
            player=nombre_jugador,
            title="",
            clase=clase,
            race=race,
            alignment=alignment,
            god=deity,
        )

        if len(RACES[race]) == 0:
            partial_pj["Subrace"] = ""
            row = PJRow.from_dict(partial_pj)
            sh.insert_row(row, sh.find_first_empty_row("A", strict=True))
            return await interaction.followup.send(
                f"Registrado {row.Name}.\nUtiliza `/set_ability_scores` para definir los Ability Scores de tu personaje,"
                f" `/set_all_skills` para definir tus skills y `set_all_saves` para definir tus saves."
            )

        heritage_dropdown = SubraceDropdown(partial_pj)

        view = RegisterDropdownView(heritage_dropdown)
        await interaction.followup.send("Selecciona una subraza para tu personaje", view=view)

    @standard_command("Edita las clases de tu personaje.")
    async def edit_class(
        self: Self,
        interaction: Interaction,
        clase: Class = SlashOption(
            name="clase",
            description="La clase de tu personaje. Selecciona una clase que ya tengas o añade una nueva.",
            required=True,
            choices=CLASSES.keys(),
        ),
        nivel: int = SlashOption(name="nivel", description="La cantidad de niveles en la clase", required=True),
        subclass: str = SlashOption(
            name="subclase",
            description="La subclase de tu personaje. Escribe el nombre de la clase para buscar las subclases.",
            required=False,
            default="",
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        subclass = subclass.split(" - ")[-1] if subclass else ""
        sh = PJsController()
        pj_row = sh.get_pj_row(user_id)
        if subclass in CLASSES[clase]:
            pj_row.Classes[clase] = (subclass, nivel)
        elif subclass == "":
            old_subclass = pj_row.Classes.get(clase, ("", 0))[0]
            pj_row.Classes[clase] = (old_subclass, nivel)
        else:
            return await interaction.followup.send(f"'{subclass}' no es una subclase válida para '{clase}'.")

        sh.update_row(pj_row)
        await interaction.followup.send(
            f"Clase {f"*{subclass}* " if subclass else ""}{clase} registrada con nivel {nivel}."
        )

    @standard_command("Elimina una clase de tu personaje.")
    async def remove_class(
        self: Self,
        interaction: Interaction,
        clase: Class = SlashOption(
            name="clase",
            description="La clase de tu personaje a eliminar.",
            required=True,
            choices=CLASSES.keys(),
        ),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj_row = sh.get_pj_row(user_id)
        if clase in pj_row.Classes:
            del pj_row.Classes[clase]
            sh.update_row(pj_row)
            await interaction.followup.send(f"Clase {clase} eliminada.")
        else:
            await interaction.followup.send(f"'{clase}' no es una clase válida para '{pj_row.Name}'.")

    @standard_command("Cambia el título de tu personaje.")
    async def set_title(
        self: Self,
        interaction: Interaction,
        title: str = SlashOption(name="titulo", description="El nuevo título de tu personaje", required=True),
    ) -> Any:
        user_id = not_none(interaction.user).id
        sh = PJsController()
        pj_row = sh.get_pj_row(user_id)
        pj_row.Title = title
        sh.update_row(pj_row)
        await interaction.followup.send(f"Título de {pj_row.Name} cambiado a '{title}'.")

    @register.on_autocomplete("race")
    async def autocomplete_ancestry(self, interaction: Interaction, ancestry: str) -> Any:
        filtered_ancestries = []
        if ancestry:
            filtered_ancestries = [a for a in RACES.keys() if a.lower().startswith(ancestry.lower())]
        await interaction.response.send_autocomplete(filtered_ancestries)

    @edit_class.on_autocomplete("subclass")
    async def autocomplete_subclasses(self, interaction: Interaction, clase: str) -> Any:
        filtered_subclasses = []
        if clase:

            filtered_subclasses = [c for c in SUBCLASSES if c.lower().startswith(clase.lower())]
        await interaction.response.send_autocomplete(filtered_subclasses)
