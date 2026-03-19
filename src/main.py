"""
Main application entry point

Initializes and runs the Telegram freelance hunter bot with:
- Telegram userbot client (Telethon) for monitoring channels
- Telegram bot (aiogram) for handling user commands
- Message filtering and forwarding to admin chat
"""

import asyncio

from src.bootstrap import bootstrap
from src.bot.bot import create_bot
from src.telegram_client.client import create_telegram_client
from src.utils.logger import logger


async def main() -> None:
    """
    Main application entry point

    Orchestrates the complete application startup:
    1. Runs bootstrap initialization (database, API connection, caches)
    2. Creates aiogram bot instance
    3. Creates Telethon userbot client
    4. Starts Telethon client for event monitoring
    5. Starts aiogram dispatcher for polling bot updates

    The application runs until interrupted (Ctrl+C)
    If bootstrap fails, the application exits without starting services

    Side effects:
        - Initializes all application services
        - Blocks until services are terminated
        - Logs application status via logger
    """

    if await bootstrap():
        bot, dp = create_bot()

        telegram_client = create_telegram_client(bot)

        await telegram_client.start()

        logger.success("Application started")

        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
