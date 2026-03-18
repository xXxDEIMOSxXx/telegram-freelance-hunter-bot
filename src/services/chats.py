"""Groups and chats"""

import json

from src.config import settings
from src.utils.logger import logger


def get_chats_data() -> list[dict]:
    """Load channels and groups configuration"""

    try:
        chats_file_path = settings.CHATS_FILE
        if not chats_file_path.is_file():
            logger.error(f"Channels/groups info file not found: {chats_file_path}")
            return []

        with chats_file_path.open(encoding="utf-8") as f:
            data = json.load(f)
            logger.success(
                f"Successfully get channels and groups ids from {chats_file_path}"
            )
            return data

    except Exception as e:
        logger.critical(f"Failed to get channels and groups ids: {e}", exc_info=True)
        return []
