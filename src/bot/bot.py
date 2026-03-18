"""Setting up aiogram bot"""

from aiogram import Bot, Dispatcher

from src.bot.handlers import cleanup, start
from src.config import settings
from src.utils.logger import logger


def create_bot() -> tuple[Bot, Dispatcher]:
    """Create and setup aiogram bot"""

    try:
        bot = Bot(token=settings.BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(start.router)
        dp.include_router(cleanup.router)
        logger.success("Bot initialized successfully")

    except Exception as e:
        logger.exception(f"Failed to initialize Bot > {e}")
        raise

    return bot, dp
