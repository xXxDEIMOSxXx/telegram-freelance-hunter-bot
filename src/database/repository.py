"""Repository for async interaction with telegram_bot_messages_history db table"""

from typing import Any, Dict

from sqlalchemy import Result, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TelegramMessage
from src.utils.logger import logger


async def save_message(session: AsyncSession, message_data: Dict[str, Any]) -> int:
    """Save message to database"""

    message_statement = (
        insert(TelegramMessage)
        .values(
            message_datetime=message_data["message_datetime"],
            chat_title=message_data["chat_title"],
            chat_id=message_data["chat_id"],
            sender_id=message_data["sender_id"],
            have_keyword=message_data["have_keyword"],
            keyword=message_data["keyword"],
            not_scum=message_data["not_scum"],
            notify=message_data["notify"],
            message_text=message_data["message_text"],
        )
        .returning(TelegramMessage.message_id)
    )

    try:
        result: Result = await session.execute(message_statement)
        await session.commit()
        inserted_id: int = result.scalar_one()
        logger.info(f"Message saved to database with ID: {inserted_id}")
        return inserted_id
    except Exception as e:
        await session.rollback()
        logger.error(f"Message saving error: {e}", exc_info=True)
        raise
