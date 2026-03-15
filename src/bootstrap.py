"""Bootstrap module - application initialization"""

from src.services.keyword_service import generate_keyword_forms
from src.utils.logger import logger


def bootstrap() -> None:
    """
    Coordinates the execution of all initialization steps.
    Calls functions from the appropriate modules.
    """

    logger.info("Bootstrap - app initialisation started...")

    try:
        generate_keyword_forms()
    except Exception:
        logger.critical("Bootstrap - app initialisation failed!")
        raise
