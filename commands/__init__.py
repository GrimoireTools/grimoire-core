from loguru import logger
from nextcord.ext.commands import Bot
from commands.resources import ResourcesCommands
from commands.attributes import AttributesCommands
from commands.register import RegisterCommands
from commands.kill import KillCommands
from commands.abilities import AbilitiesCommands
from commands.roll import RollCommands


def setup_all_commands(bot: Bot):
    """
    This function is used to set up all commands in the bot.
    It imports all command modules and registers them with the bot.
    """
    command_classes = [
        RegisterCommands,
        KillCommands,
        ResourcesCommands,
        AttributesCommands,
        AbilitiesCommands,
        RollCommands,
    ]

    for command_class in command_classes:
        logger.info(f"Setting up {command_class.__name__}...")
        command_class.setup(bot)
