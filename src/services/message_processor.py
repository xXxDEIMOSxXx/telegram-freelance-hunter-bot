"""Message processor service

Handles incoming Telegram messages by:
1. Extracting message text and metadata
2. Checking for keywords and blacklist status
3. Determining if notification should be sent
4. Persisting message data to database"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.database.repository import save_message
from src.services.blacklist import get_blacklist
from src.services.keywords import get_keywords
from src.utils.logger import logger


async def process_message(
    event: Any, chat_link: str, session: AsyncSession
) -> dict[str, Any]:
    """
    Process incoming Telegram message and determine if notification needed.

    Performs the following checks:
    1. Extracts message text from event
    2. Searches for keywords in the message
    3. Checks if sender is blacklisted
    4. Determines notification eligibility (has keyword AND not blacklisted)
    5. Saves message data to database
    6. Returns appropriate response with notification flag

    Args:
        event: Telethon NewMessage event object containing:
            - raw_text: Message text content
            - sender_id: User ID of message sender (can be None for restricted channels)
            - chat: Chat object with title and id
        chat_link: URL/link to the chat where message originated
        session: AsyncSession for database operations

    Returns:
        dict[str, Any]: Response dictionary containing:
            - notify: Boolean flag indicating if bot should send notification
            - keyword: (if notify=True) The matched keyword
            - text: (if notify=True) Full message text
            - chat_title: (if notify=True) Title of the source chat
            - chat_link: (if notify=True) Link to the chat

    Side effects:
        - Saves message to database via save_message()
        - Logs processed message with relevant metadata
        - Modifies database state

    Notes:
        - sender_id defaults to 0 for restricted channels (prevents system errors)
        - Messages with no keywords or blacklisted senders are not notified
        - Uses keyword forms detection (Ukrainian/Russian/English morphology)
    """

    text = event.raw_text or ""

    have_keyword, keyword = get_keywords.find_keyword_in_message_text(text)

    sender_id = event.sender_id or 0
    # 0 - because in case of restricted chanel - we can't get user id or
    # sometimes even chat id - then use 0 to prevent system error

    not_scum = not get_blacklist.is_blacklisted(sender_id)

    notify = have_keyword and not_scum

    message_data = {
        "message_datetime": func.now(),  # pylint: disable=not-callable
        "chat_title": event.chat.title or "-",
        "chat_id": int(event.chat.id),
        "sender_id": int(sender_id) if sender_id else "0",
        "have_keyword": have_keyword,
        "keyword": keyword or "-",
        "not_scum": not_scum,
        "notify": notify,
        "message_text": text,
    }

    await save_message(session=session, message_data=message_data)

    if notify:
        logger.info(
            "✓ Message processed | chat=%s | sender_id=%s | not_scum=%s | "
            "keyword=%s | notify=%s | text=%s",
            event.chat.title,
            sender_id,
            not_scum,
            have_keyword,
            notify,
            text,
        )

        return {
            "notify": True,
            "keyword": keyword,
            "text": text,
            "chat_title": event.chat.title,
            "chat_link": chat_link,
        }

    text_trunc = ((text[:50] + "...") if len(text) > 50 else text).replace("\n", " ")

    logger.info(
        "× Message processed | chat=%s | sender_id=%s | not_scum=%s | "
        "keyword=%s | notify=%s | text=%s",
        event.chat.title,
        sender_id,
        not_scum,
        have_keyword,
        notify,
        text_trunc,
    )

    return {"notify": False}
