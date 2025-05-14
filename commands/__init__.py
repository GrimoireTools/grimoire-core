from loguru import logger
from nextcord.ext.commands import Bot
from commands.consent_form import ConsentFormCommands
from commands.delete_character import DeleteCharacterCommands
from commands.downtime import DowntimeCommands
from commands.earn_income import EarnIncomeCommands
from commands.formulas import FormulasCommands
from commands.languages import LanguagesCommands
from commands.money import MoneyCommands
from commands.new_character import NewCharacterCommands
from commands.saves import SaveCommands
from commands.skills import SkillCommands
from commands.victory_points import VictoryPointsCommands
from commands.info import InfoCommands
from commands.salary import SalaryCommands


def setup_all_commands(bot: Bot):
    """
    This function is used to set up all commands in the bot.
    It imports all command modules and registers them with the bot.
    """
    command_classes = [
        EarnIncomeCommands,
        LanguagesCommands,
        MoneyCommands,
        NewCharacterCommands,
        SaveCommands,
        SkillCommands,
        VictoryPointsCommands,
        FormulasCommands,
        DowntimeCommands,
        DeleteCharacterCommands,
        InfoCommands,
        SalaryCommands,
        ConsentFormCommands,
    ]

    for command_class in command_classes:
        logger.info(f"Setting up {command_class.__name__}...")
        command_class.setup(bot)
