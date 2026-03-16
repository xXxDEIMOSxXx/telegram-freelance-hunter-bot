"""
Service that filtered messages
If user id in blacklist - program skip this user message
"""

import json

from src.config import settings
from src.utils.logger import logger


def get_blacklist_values() -> set[int]:
    """Load blacklist values from blacklist.json"""

    try:
        blacklist_path = settings.BLACKLIST_FILE
        if not blacklist_path.exists():
            logger.error(f"Blacklist file not found: {blacklist_path}")
            return set()

        with blacklist_path.open(encoding="utf-8") as f:
            data = json.load(f)
            blacklist = {value["user_id"] for value in data}

        if blacklist:
            logger.info("Blacklist loaded successfully")
        else:
            logger.error("No blacklist values found in file")

        return blacklist

    except Exception as e:
        logger.error(f"Failed to get blacklist values: {e}", exc_info=True)
        return set()
