"""Main module"""

import asyncio

from src.bootstrap import bootstrap
from src.bot.bot import create_bot
from src.telegram_client.client import create_telegram_client
from src.utils.logger import logger


async def main():
    """Main function"""

    if await bootstrap():
        bot, dp = create_bot()

        telegram_client = create_telegram_client(bot)

        await telegram_client.start()

        logger.success("Application started")

        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
