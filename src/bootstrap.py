"""Application bootstrap module

Coordinates initialization of all application components including:
- Telegram API connection validation
- Database initialization
- Keyword cache preloading
- Blacklist cache preloading
"""

from src.database.connection import init_database
from src.services.blacklist import get_blacklist
from src.services.keywords import get_keywords
from src.services.network import check_telegram_api_connection
from src.utils.logger import logger


async def bootstrap() -> bool:
    """
    Coordinate initialization of all application components

    Performs startup checks and initialization in sequence:
    1. Validates Telegram API connection
    2. Initializes PostgreSQL database
    3. Preloads keyword forms cache
    4. Preloads blacklist cache

    All steps must complete successfully for the application to start

    Returns:
        bool: True if all bootstrap steps succeed, False otherwise

    Side effects:
        - Validates and initializes Telegram connection
        - Creates database tables if needed
        - Loads keyword forms from JSON to memory cache
        - Loads blacklist from JSON to memory cache
        - Logs bootstrap progress and errors via logger

    Notes:
        - If any initialization step fails, bootstrap fails immediately
        - Failures are logged with details but not re-raised
        - Application should not proceed if bootstrap returns False
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
        logger.critical("Bootstrap - app initialisation failed %s", e)
        return False
