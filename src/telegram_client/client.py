"""Telegram client initialization using Telethon

Creates and configures the Telethon client for monitoring Telegram channels/groups
as a user account. Handles message event registration and connection management
"""

from typing import Any

from telethon import TelegramClient

from src.config import settings
from src.telegram_client.handlers.new_message import register_message_handler


def create_telegram_client(bot: Any) -> TelegramClient:
    """
    Create and configure a Telethon Telegram client

    Initializes the Telethon client with:
    - API credentials from settings
    - Language configuration
    - Connection retry strategy
    - Message event handler registration

    Args:
        bot: The aiogram bot instance to pass to message handlers

    Returns:
        TelegramClient: Configured Telethon client ready to connect

    Side effects:
        - Registers message handler via register_message_handler()
        - Creates session file "session" for connection state persistence

    Notes:
        - Connection retry: 360 attempts * 10 seconds = 1 hour reconnection window
        - Session file persists authentication state across restarts
    """

    client = TelegramClient(
        session="session",
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        lang_code=settings.LANG_CODE,
        system_lang_code=settings.SYSTEM_LANG_CODE,
        connection_retries=360,  # 360 * 10 / 60 - trying to reconnect for 1 hour
        retry_delay=10,
    )

    register_message_handler(client, bot)

    return client
