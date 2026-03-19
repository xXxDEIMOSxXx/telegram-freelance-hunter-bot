"""Chat/group configuration management

Loads monitored Telegram chats and groups configuration from JSON file.
"""

import json

from src.config import settings
from src.utils.logger import logger


def get_chats_data() -> list[dict]:
    """
    Load monitored channels and groups configuration from JSON file.

    Reads the chats configuration file and returns the list of chat entries.
    Each entry contains chat metadata (ID, title, etc.) for the bot to monitor.

    Expected JSON structure:
        [
            {"id": 123456789, "name": "Channel Name"},
            {"id": 987654321, "tame": "Group Name"}
        ]

    Returns:
        list[dict]: List of chat configuration dictionaries, or empty list
                   if file not found or JSON parsing fails

    Side effects:
        - Logs success message on successful load
        - Logs error/critical message on failure
        - Returns empty list on any error (graceful degradation)
    """

    try:
        chats_file_path = settings.CHATS_FILE
        if not chats_file_path.is_file():
            logger.error("Channels/groups info file not found: %s", chats_file_path)
            return []

        with chats_file_path.open(encoding="utf-8") as f:
            data = json.load(f)
            logger.success(
                f"Successfully get channels and groups ids from {chats_file_path}"
            )
            return data

    except Exception as e:
        logger.critical("Failed to get channels and groups ids: %s", e, exc_info=True)
        return []
