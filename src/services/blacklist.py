"""Blacklist service for filtering messages by sender

Manages user blacklist to prevent notifications from known spam/scam senders.
Uses JSON file-based storage with in-memory caching for performance.
"""

import json

from src.config import settings
from src.utils.logger import logger

# ToDo for future: as an improvement use redis/etc or other more advanced caching methods # pylint: disable=fixme


class BlacklistService:
    """
    Blacklist service for managing spam/scam user IDs.

    Loads blacklisted user IDs from a JSON file and caches them in memory.
    Provides fast O(1) lookup to check if a user is blacklisted.

    Attributes:
        _cache: Set of blacklisted user IDs, or None if not yet loaded
    """

    def __init__(self) -> None:
        """Initialize blacklist service with empty cache"""
        self._cache: set[int] | None = None

    def _load(self) -> None:
        """
        Load blacklist from JSON file into memory cache (lazy load).

        Reads the blacklist JSON file and extracts user IDs into a set for
        fast membership checking. Only loads once - subsequent calls check
        if already loaded.

        Expected JSON structure:
            [
                {"user_id": 123456789},
                {"user_id": 987654321}
            ]

        Side effects:
            - Populates self._cache with user IDs
            - Logs success/error messages via logger
            - Creates empty set if file missing or JSON invalid
        """

        if self._cache is not None:
            return

        try:
            path = settings.BLACKLIST_FILE
            if not path.exists():
                logger.error("Blacklist file not found: %s", path)
                self._cache = set()
                return

            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            self._cache = {value["user_id"] for value in data}
            logger.success("Blacklist loaded successfully")
        except Exception as e:
            logger.critical(
                "Bootstrap - app initialisation failed: %s", e, exc_info=True
            )
            self._cache = set()

    def is_blacklisted(self, user_id: int) -> bool:
        """
        Check if a user ID is in the blacklist.

        Performs lazy loading if cache not yet populated.

        Args:
            user_id: Telegram user ID to check

        Returns:
            bool: True if user is blacklisted, False otherwise

        Side effects:
            - Calls _load() if cache not initialized
            - Logs warning if loading occurs
        """

        if self._cache is None:
            logger.warning("Blacklist cache is empty - loading now")
            self._load()
        return user_id in self._cache

    def preload(self) -> None:
        """
        Force preload blacklist at application startup.

        Ensures blacklist is loaded before any message processing begins.
        Called during bootstrap to avoid lazy loading delays.

        Side effects:
            - Calls _load() to populate cache
            - Logs any errors that occur
        """

        if self._cache is None:
            self._load()


get_blacklist = BlacklistService()
