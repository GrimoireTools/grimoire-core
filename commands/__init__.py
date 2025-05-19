from loguru import logger
from nextcord.ext.commands import Bot
from commands.downtime import DowntimeCommands
from commands.money import MoneyCommands
from commands.new_character import NewCharacterCommands
from commands.resources import ResourcesCommands
from commands.saves import SaveCommands
from commands.skills import SkillCommands
from commands.info import InfoCommands
from commands.salary import SalaryCommands
from commands.attributes import AttributesCommands


def setup_all_commands(bot: Bot):
    """
    This function is used to set up all commands in the bot.
    It imports all command modules and registers them with the bot.
    """
    command_classes = [
        AttributesCommands,
        DowntimeCommands,
        InfoCommands,
        MoneyCommands,
        NewCharacterCommands,
        ResourcesCommands,
        SalaryCommands,
        SaveCommands,
        SkillCommands,
    ]

    for command_class in command_classes:
        logger.info(f"Setting up {command_class.__name__}...")
        command_class.setup(bot)
