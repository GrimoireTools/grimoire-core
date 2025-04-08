from typing import Self, Any
from PF2eData import ITEM_CATEGORIES
from controllers.formulas_controller import FormulaRow, FormulasController
from controllers.lib.cog import standard_command, Cog
from nextcord import Interaction, SlashOption


class FormulasCommands(Cog):

    @standard_command("Muestra la lista de formulas disponibles")
    async def global_formulas(
        self: Self,
        interaction: Interaction,
        level: int = SlashOption(
            "item_level", "Nivel de los items de las formulas (-1 para Varios)", False, min_value=-1, max_value=25
        ),
    ) -> Any:

        formulas = FormulasController().get_all_rows()
        if len(formulas) == 0:
            await interaction.followup.send("No hay formulas globales")
        message = f"**Todas las formulas públicas{f" de nivel {level}" if level is not None else ""}:**"
        if level is not None:
            _level = "Varios" if level == -1 else str(level)
            formulas = [r for r in formulas if r.Item_level == _level]
        formulas.sort(key=(lambda r: r.Item_name))
        formulas.sort(key=(lambda r: r.Item_name))
        for r in formulas:
            message += f"\n- (Lvl {r.Item_level}) {r.Item_name}"
            if len(message) >= 1800:
                message += "\n\n .... El resto de formulas no caben en el mensaje"
                break
        return await interaction.followup.send(message)

    @standard_command("Añade una formula a la lista de formulas globales")
    async def add_formula(
        self: Self,
        interaction: Interaction,
        item_name: str = SlashOption("item", "Nombre del item de la formula", True),
        item_level: str = SlashOption("level", "Nivel del item de la formula", True),
        item_rarity: str = SlashOption(
            "rarity", "Rareza del item de la formula", True, choices=["Common", "Uncommon", "Rare", "Unique"]
        ),
        item_type: str = SlashOption("type", "Tipo del item de la formula", True, choices=ITEM_CATEGORIES),
        item_requirements: str = SlashOption(
            "requirements", "Requerimientos para la creación del item", False, default=""
        ),
    ) -> Any:
        sh_formulas = FormulasController()
        formulas = sh_formulas.get_all_rows()
        formula_names = [r.Item_name for r in formulas]
        if item_name in formula_names:
            await interaction.followup.send(f"*{item_name}* ya está registrado en la lista de formulas globales")
        else:
            sh_formulas.insert_row(
                FormulaRow(
                    Item_name=item_name,
                    Rarity=item_rarity,
                    Type=item_type,
                    Item_level=item_level,
                    Requirements=item_requirements,
                )
            )
            await interaction.followup.send(f"*{item_name}* se registró en la lista de formulas globales")
