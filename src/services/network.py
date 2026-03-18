"""Service that check internet connection before bot starting"""

from aiohttp import ClientSession, ClientTimeout

from src.config import settings
from src.utils.logger import logger


async def check_telegram_api_connection() -> None:
    """Check if Telegram API is accessible using bot token"""

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getMe"
    timeout = ClientTimeout(total=3)

    # ToDo make better error catch  # pylint: disable=fixme
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        logger.success("Telegram API is accessible")
                    else:
                        logger.warning("Telegram API responded, but returned not ok")
                else:
                    logger.error(f"Telegram API error > {response.status}")
    except Exception as e:
        logger.error(f"Telegram API check failed: {e}")
