"""Bot cleanup func"""

import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove

from src.utils.logger import logger

router = Router()

MAX_DELETE_ATTEMPTS: int = 50  # delete limit
DELETE_DELAY: float = 0.30


@router.message(F.text.lower() == "clear history")
async def cmd_cleanup(message: Message) -> None:
    """/clean history command"""

    user_id = message.from_user.id
    chat_id = message.chat.id

    deleted_count = 0

    logger.info(f"Cleanup requested from user > {user_id} in chat: {chat_id}")

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

                logger.warning(f"Cant' delete message with id > {msg_id}: {e}")
                break

        await message.answer(
            f"Deleted {deleted_count} messages from chat history",
            reply_markup=ReplyKeyboardRemove(),
        )

    except Exception as e:
        logger.error(f"Error while clearing history: {e}", exc_info=True)
        await message.answer("An error occurred while cleaning. Please try again later")
