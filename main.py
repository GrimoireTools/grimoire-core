from loguru import logger

from nextcord.ext import commands  # type: ignore
import sys
from commands import setup_all_commands
from controllers.salary_controller import update_level_global
from varenv import getVar
from icecream import install, ic

# Logging
logger.remove()
logger.add(sys.stderr, colorize=True)
install()
ic.configureOutput(includeContext=True)

BOT_TOKEN = getVar("TOKEN")

bot = commands.Bot()


@bot.event
async def on_ready() -> None:
    logger.info(f"We have logged in as {bot.user}")
    update_level_global()
    logger.info("Bot is ready")


logger.info("Setting up commands...")
setup_all_commands(bot)

logger.info("Commands setup complete. Starting bot...")


bot.run(BOT_TOKEN)
