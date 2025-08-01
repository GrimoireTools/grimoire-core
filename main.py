"""
Main entry point for the costilla-bot Discord bot.

This module initializes logging, configures the bot, loads commands, and starts the bot.
It uses Nextcord for Discord integration and Loguru for logging.

Example:
    Run this file to start the bot:
    ```bash
    python main.py
    ```

Important classes/functions:
    - setup_all_commands: Loads all bot commands.
    - get_var: Retrieves environment variables.
    - bot: The Discord bot instance.
"""
from loguru import logger

from nextcord.ext import commands  # type: ignore
import sys
from commands import setup_all_commands
from varenv import get_var
from icecream import install, ic

# Logging
logger.remove()
logger.add(sys.stderr, colorize=True)
install()
ic.configureOutput(includeContext=True)

BOT_TOKEN = get_var("TOKEN")

bot = commands.Bot()


@bot.event
async def on_ready() -> None:
    """Event triggered when the bot is ready."""
    logger.info(f"We have logged in as {bot.user}")
    logger.info("Bot is ready")


logger.info("Setting up commands...")
setup_all_commands(bot)

logger.info("Commands setup complete. Starting bot...")


bot.run(BOT_TOKEN)
