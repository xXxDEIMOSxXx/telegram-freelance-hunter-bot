"""Message processor"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.database.repository import save_message
from src.services.blacklist import get_blacklist
from src.services.keywords import get_keywords
from src.utils.logger import logger


async def process_message(
    event, chat_link: str, session: AsyncSession
) -> dict[str, bool]:
    """Process message func"""

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
            f"✓ Message processed | chat={event.chat.title} | sender_id={sender_id} "
            f"| not_scum={not_scum} | keyword={have_keyword} | notify={notify} | text={text}"
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
        f"× Message processed | chat={event.chat.title} | sender_id={sender_id} "
        f"| not_scum={not_scum} | keyword={have_keyword} | notify={notify} | text={text_trunc}"
    )

    return {"notify": False}
