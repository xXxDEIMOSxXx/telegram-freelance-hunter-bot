"""Bot message history cleanup handler

Handles "Clear history" button press to delete recent bot messages from chat.
"""

import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove

from src.utils.logger import logger

router = Router()

MAX_DELETE_ATTEMPTS: int = 50  # Maximum messages to attempt deletion
DELETE_DELAY: float = (
    0.30  # Delay between delete requests (seconds) to prevent API flood
)


@router.message(F.text.lower() == "clear history")
async def cmd_cleanup(message: Message) -> None:
    """
    Handle "Clear history" button press to delete recent messages.

    Attempts to delete up to MAX_DELETE_ATTEMPTS messages backwards from
    the current message. Handles various error cases gracefully:
    - Already deleted messages are skipped
    - Old messages that can't be deleted (too old) stop the process
    - Other errors are logged and operation is halted

    Uses DELETE_DELAY between requests to prevent Telegram API flooding.

    Args:
        message: Aiogram Message object from the "Clear history" button press

    Side effects:
        - Sends deletion status response to user
        - Deletes up to MAX_DELETE_ATTEMPTS messages from chat
        - Logs cleanup operation and any errors
        - Removes reply keyboard after operation
        - On error, sends error message to user
    """

    user_id = message.from_user.id
    chat_id = message.chat.id

    deleted_count = 0

    logger.info("Cleanup requested from user > %s in chat: %s", user_id, chat_id)

    try:
        for msg_id in range(
            message.message_id, message.message_id - MAX_DELETE_ATTEMPTS, -1
        ):  # find last bot messages
            try:
                await message.bot.delete_message(chat_id, msg_id)
                deleted_count += 1
                await asyncio.sleep(DELETE_DELAY)  # prevent flood
            except TelegramBadRequest as e:
                if (
                    "message to delete not found" in str(e).lower()
                ):  # message already deleted
                    continue
                if "can't delete message" in str(e).lower():  # old messages
                    break

                logger.warning("Can't delete message with id > %s: %s", msg_id, e)
                break

        await message.answer(
            f"Deleted {deleted_count} messages from chat history",
            reply_markup=ReplyKeyboardRemove(),
        )

    except Exception as e:
        logger.error("Error while clearing history: %s", e, exc_info=True)
        await message.answer("An error occurred while cleaning. Please try again later")
