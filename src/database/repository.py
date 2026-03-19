"""Repository for async interaction with telegram_bot_messages_history database table

This module provides data access layer for persisting Telegram messages
to the PostgreSQL database
"""

from typing import Any, Dict

from sqlalchemy import Result, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TelegramMessage
from src.utils.logger import logger


async def save_message(session: AsyncSession, message_data: Dict[str, Any]) -> int:
    """
    Save a Telegram message to the database

    Persists message metadata and content to the telegram_bot_messages_history table
    Automatically commits the transaction on success or rolls back on failure

    Args:
        session: AsyncSession instance for database operations
        message_data: Dictionary containing message fields:
            - message_datetime: Message timestamp (datetime with timezone)
            - chat_title: Title of the chat/channel
            - chat_id: Telegram chat ID
            - sender_id: Telegram sender/user ID
            - have_keyword: Boolean indicating if keywords were found
            - keyword: Matched keyword string (or "-" if none)
            - not_scum: Boolean indicating if sender is not blacklisted
            - notify: Boolean indicating if bot should notify
            - message_text: Full message text content

    Returns:
        int: The auto-generated message_id of the saved message

    Raises:
        Exception: If database operation fails (logged with traceback)

    Side effects:
        - Commits changes to database on success
        - Rolls back transaction on exception
        - Logs info message on success with inserted message ID
        - Logs error with traceback on failure
    """

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
        logger.info("Message saved to database with ID: %s", inserted_id)
        return inserted_id
    except Exception as e:
        await session.rollback()
        logger.error("Message saving error: %s", e, exc_info=True)
        raise
