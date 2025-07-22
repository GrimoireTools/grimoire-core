"""Commands package for the Costilla Bot Discord application.

This package contains all command modules and provides a centralized setup
function to register all commands with the bot instance.

The package includes various command categories:
- Character management (new, delete)
- Economic systems (money, income, salary)
- Game mechanics (skills, saves, victory points)
- Utility functions (formulas, info, languages)
- Administrative tools (announcements, consent forms)

Example:
    ```python

    bot = Bot(command_prefix='!')
    setup_all_commands(bot)
    ```
"""

from loguru import logger
from nextcord.ext.commands import Bot
from commands.announcements import AnnouncementsCommands
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


def setup_all_commands(bot: Bot) -> None:
    """
    Set up all commands in the bot.

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
        AnnouncementsCommands,
    ]

    for command_class in command_classes:
        logger.info(f"Setting up {command_class.__name__}...")
        command_class.setup(bot)
