"""Bootstrap module - application initialization"""

from src.database.connection import init_database
from src.services.blacklist import get_blacklist
from src.services.keywords import get_keywords
from src.services.network import check_telegram_api_connection
from src.utils.logger import logger


async def bootstrap() -> bool:
    """
    Coordinates the execution of all initialization steps
    Calls functions from the appropriate modules
    """

    logger.info("Bootstrap - app initialisation started...")

    try:
        await check_telegram_api_connection()
        await init_database()
        get_keywords.preload()
        get_blacklist.preload()
        logger.success("Bootstrap - app initialisation successfully completed")
        return True
    except Exception as e:
        logger.critical(f"Bootstrap - app initialisation failed {e}")
        return False
