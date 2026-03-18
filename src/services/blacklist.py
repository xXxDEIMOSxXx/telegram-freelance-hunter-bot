"""
Service that filtered messages
If user id in blacklist - program skip this user message
"""

import json

from src.config import settings
from src.utils.logger import logger

# ToDo for future: as an improvement use redis/etc or other more advanced caching methods # pylint: disable=fixme


class BlacklistService:
    """Blacklist service class"""

    def __init__(self):
        self._cache: set[int] | None = None

    def _load(self) -> None:
        """Load blacklist one time > to cache"""
        if self._cache is not None:
            return

        try:
            path = settings.BLACKLIST_FILE
            if not path.exists():
                logger.error(f"Blacklist file not found: {path}")
                self._cache = set()
                return

            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            self._cache = {value["user_id"] for value in data}
            logger.success("Blacklist loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load blacklist: {e}", exc_info=True)
            self._cache = set()

    def is_blacklisted(self, user_id: int) -> bool:
        """Check if user id is blacklisted"""
        if self._cache is None:
            logger.warning("Blacklist cache is empty - loading now")
            self._load()
        return user_id in self._cache

    def preload(self) -> None:
        """Force load blacklist at startup"""

        if self._cache is None:
            self._load()


get_blacklist = BlacklistService()
