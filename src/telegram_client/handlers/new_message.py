"""Telethon new message event handler

Registers and handles new messages from monitored Telegram chats/channels.
Processes messages for keywords and forwards relevant ones to admin chat.
"""

from typing import Any

from aiogram import Bot
from telethon import TelegramClient, events

from src.config import settings
from src.database.connection import async_session
from src.services.chats import get_chats_data
from src.services.message_processor import process_message
from src.utils.logger import logger


def register_message_handler(client: TelegramClient, bot: Bot) -> None:
    """
    Register and initialize new message event handler for monitored chats.

    Sets up a Telethon event listener that:
    1. Monitors specified chats for new messages
    2. Processes each message for keywords/blacklist
    3. Forwards qualifying messages to admin chat via aiogram bot
    4. Prevents duplicate processing with simple key tracking

    The handler uses cached chat data to map chat IDs to URLs for fast lookup.
    Processed messages are tracked to prevent double-processing.

    Args:
        client: Telethon TelegramClient instance for event listening
        bot: aiogram Bot instance for sending notifications

    Side effects:
        - Registers event handler on the Telethon client
        - Loads chat configuration from file
        - Creates in-memory processed message cache
        - Messages matching criteria are sent to BOT_CHAT_ID

    Notes:
        - Processed set persists in memory (not shared across restarts)
        - Uses simple (chat_id, message_id) key for duplicate detection
        - All errors are caught and logged (non-fatal)
    """

    chats_data = get_chats_data()

    chat_map: dict[int, str] = {
        int(chat["chat_id"]): chat["url"]
        for chat in chats_data
        if "chat_id" in chat and "url" in chat
    }

    chat_ids: list[int] = list(chat_map.keys())

    processed: set[tuple[int, int]] = set()

    @client.on(events.NewMessage(chats=chat_ids))
    async def handler(event: events.NewMessage.Event) -> None:
        """
        Handle new message event from monitored chats.

        Args:
            event: Telethon NewMessage event containing message and chat info
        """

        key: tuple[int, int] = (
            event.chat_id,
            event.id,
        )  # simple double message protection
        if key in processed:
            return
        processed.add(key)

        try:
            chat_link = chat_map.get(event.chat.id)
            async with async_session() as session:  # create session
                async with session.begin():
                    result: dict[str, Any] = await process_message(
                        event, chat_link, session=session
                    )
                    if result["notify"]:
                        await bot.send_message(
                            settings.BOT_CHAT_ID,
                            f"<b>FROM CHAT:</b>\n{result['chat_title']}\n\n"
                            f"<b>KEYWORD:</b>\n{result['keyword']}\n\n"
                            f"<b>TEXT:</b>\n{result['text']}",
                            parse_mode="HTML",
                        )

                        logger.info("Message notified (sended to bot chat)")

        except Exception as e:
            logger.error("Message handler error %s", e, exc_info=True)
