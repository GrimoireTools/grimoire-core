from loguru import logger

from nextcord.ext import commands  # type: ignore
import sys
from commands import setup_all_commands
from varenv import get_env
from icecream import ic
from controllers.pjs_controller import PJsController

# Logging
logger.remove()
logger.add(sys.stderr, colorize=True)
ic.configureOutput(includeContext=True)

BOT_TOKEN = get_env("TOKEN")

bot = commands.Bot()


@bot.event
async def on_ready() -> None:
    logger.info(f"We have logged in as {bot.user}")
    await bot.sync_application_commands()
    logger.info("Bot is ready")


# Load PJs
PJsController()

logger.info("Setting up commands...")
setup_all_commands(bot)

logger.info("Commands setup complete. Starting bot...")


bot.run(BOT_TOKEN)
