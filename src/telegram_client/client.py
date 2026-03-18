"""Telegram client"""

from telethon import TelegramClient

from src.config import settings
from src.telegram_client.handlers.new_message import register_message_handler


def create_telegram_client(bot):
    """Create telegram client"""

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
