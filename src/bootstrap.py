"""Bootstrap module - application initialization"""

from src.database.connection import init_database
from src.services.blacklist_service import get_blacklist_values
from src.services.keyword_service import generate_keyword_forms
from src.services.network_service import check_telegram_api_connection
from src.utils.logger import logger


async def bootstrap() -> None:
    """
    Coordinates the execution of all initialization steps.
    Calls functions from the appropriate modules.
    """

    logger.info("Bootstrap - app initialisation started...")

    try:
        await check_telegram_api_connection()
        await init_database()
        generate_keyword_forms()
        get_blacklist_values()
        logger.info("Bootstrap - app initialisation successfully completed!")
    except Exception:
        logger.critical("Bootstrap - app initialisation failed!")
        raise
