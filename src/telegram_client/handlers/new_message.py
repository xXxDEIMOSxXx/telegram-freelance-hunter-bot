"""New message handler"""

from aiogram import Bot
from telethon import TelegramClient, events

from src.config import settings
from src.database.connection import async_session
from src.services.chats import get_chats_data
from src.services.message_processor import process_message
from src.utils.logger import logger


def register_message_handler(client: TelegramClient, bot: Bot) -> None:
    """Registers a new message handler in the specified chats
    Uses cached chat data for fast link lookup"""

    chats_data = get_chats_data()

    chat_map = {
        int(chat["chat_id"]): chat["url"]
        for chat in chats_data
        if "chat_id" in chat and "url" in chat
    }
    chat_ids = list(chat_map.keys())

    processed = set()

    @client.on(events.NewMessage(chats=chat_ids))
    async def handler(event: events.NewMessage.Event) -> None:
        key = (event.chat_id, event.id)  # simple double message protection
        if key in processed:
            return
        processed.add(key)

        try:
            chat_link = chat_map.get(event.chat.id)
            async with async_session() as session:  # create session
                async with session.begin():
                    result = await process_message(event, chat_link, session=session)
                    if result["notify"]:
                        await bot.send_message(
                            settings.BOT_CHAT_ID,
                            f"<b>FROM CHAT:</b>\n{result['chat_title']}\n\n"
                            f"<b>KEYWORD:</b>\n{result['keyword']}\n\n"
                            f"<b>TEXT:</b>\n{result['text']}",
                            parse_mode="HTML",
                        )

                        logger.info("Message sent to bot")

        except Exception as e:
            logger.error(f"Message handler error {e}", exc_info=True)
