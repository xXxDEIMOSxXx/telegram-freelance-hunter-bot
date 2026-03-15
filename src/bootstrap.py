"""Bootstrap module - application initialization"""

from src.database.connection import init_database
from src.services.keyword_service import generate_keyword_forms
from src.utils.logger import logger


async def bootstrap() -> None:
    """
    Coordinates the execution of all initialization steps.
    Calls functions from the appropriate modules.
    """

    logger.info("Bootstrap - app initialisation started...")

    try:
        generate_keyword_forms()
        await init_database()
        logger.info("Bootstrap - app initialisation successfully completed!")
    except Exception:
        logger.critical("Bootstrap - app initialisation failed!")
        raise
