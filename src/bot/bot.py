"""Bot initialization using aiogram framework

Creates and configures the aiogram bot dispatcher with message handlers
for handling user commands and interactions
"""

from aiogram import Bot, Dispatcher

from src.bot.handlers import cleanup, start
from src.config import settings
from src.utils.logger import logger


def create_bot() -> tuple[Bot, Dispatcher]:
    """
    Create and configure the aiogram bot with dispatcher

    Initializes:
    - Bot instance with token from settings
    - Dispatcher for routing messages and commands
    - Message routers (start and cleanup handlers)

    Returns:
        tuple[Bot, Dispatcher]: Tuple containing:
            - Bot: Configured aiogram Bot instance
            - Dispatcher: Configured dispatcher with registered routers

    Raises:
        Exception: If bot initialization fails (exception is logged and re-raised)

    Side effects:
        - Logs success message on successful initialization
        - Logs exception if initialization fails
    """

    try:
        bot = Bot(token=settings.BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(start.router)
        dp.include_router(cleanup.router)
        logger.success("Bot initialized successfully")

    except Exception as e:
        logger.exception("Failed to initialize Bot > %s", e)
        raise

    return bot, dp
