from typing import Any, Self
from nextcord import SlashOption, Member, Interaction

from controllers.pjs_controller import PJRow, PJsController
from controllers.lib.utils import not_none, parse_float_arg
from controllers.lib.cog import Cog, standard_command
from commands.utils.caliban_utils import *


class MoneyCommands(Cog):

    @standard_command("Resta dinero de tu cuenta. Puedes transferir a otra persona.")
    async def pay(
        self: Self,
        interaction: Interaction,
        amount_str: str = SlashOption("money-gp", "Dinero restado a tu cuenta, en gp", True),
        transfertarget: Member = SlashOption(
            "target-transferencia",
            "Usuario al que se le transfiere el dinero",
            False,
            default=None,
        ),
    ) -> Any:
        amount = parse_float_arg(amount_str)
        if amount < 0:
            return await interaction.send("Debes pagar una cantidad positiva de dinero")

        sh = PJsController()

        user_id: int = not_none(interaction.user).id
        pj = sh.get_pj_row(user_id)

        total = pj.calc_money()
        if amount > total:
            return await interaction.send("No tienes suficiente dinero para esta transacción")

        pj_coins = sh.set_money(user_id, total - amount)

        transfer_id = transfertarget.id if transfertarget else None
        if transfer_id == user_id:
            await interaction.send("No puedes transferirte dinero a ti mismo")
            return await caliban_force_speaks(interaction, "Wao, dinero infinito")

        target_pj = sh.get_pj_row(transfertarget.id) if transfertarget else None

        if target_pj is not None and transfer_id is not None:
            target_total = target_pj.calc_money()
            target_pj_coins = sh.set_money(transfer_id, target_total + amount)
            msg = (
                f"{pj.Name} le paga {amount:.2f}gp a {target_pj.Name}.\n"
                f"Dinero restante de {pj.Name}: {pj_coins.pretty_print()}, **Total: {pj_coins.total():.2f}gp**\n"
                f"Dinero restante de {target_pj.Name}: {target_pj_coins.pretty_print()}, **Total: {target_pj_coins.total():.2f}gp**"
            )
        else:
            msg = (
                f"{pj.Name} paga {amount:.2f}gp.\n"
                f"Dinero restante: {pj_coins.pretty_print()}, **Total: {pj_coins.total():.2f}gp**"
            )
        await interaction.send(msg)
        await caliban_speaks(interaction, 10, "money")

    @standard_command("Suma dinero a tu cuenta.")
    async def addmoney(
        self: Self,
        interaction: Interaction,
        amount_str: str = SlashOption("money-gp", "Dinero añadido a tu cuenta, en gp", True),
        target: Member = SlashOption(
            "usuario-target",
            "Usuario al que se le añade el dinero",
            False,
            default=None,
        ),
    ) -> Any:
        amount = parse_float_arg(amount_str)
        if amount < 0:
            return await interaction.send("Debes añadir una cantidad positiva de dinero")

        user_id: int = target.id if target is not None else interaction.user.id
        sh = PJsController()
        pj: PJRow = sh.get_pj_row(user_id)
        coins = sh.set_money(user_id, pj.calc_money() + amount)

        return await interaction.followup.send(
            (f"{pj.Name} obtiene {amount:.2f}gp. Ahora tiene {coins.pretty_print()}, **Total: {coins.total():.2f}gp**")
        )
