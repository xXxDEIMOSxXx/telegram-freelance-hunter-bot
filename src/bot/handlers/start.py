"""Bot /start command handler

Handles user /start command with welcome message and keyboard.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.utils.logger import logger

router = Router()

# ToDo make nice inline keyboard, change start message  # pylint: disable=fixme


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Handle /start command from user.

    Sends welcome message and displays reply keyboard with cleanup option.

    Args:
        message: Aiogram Message object containing user info and chat context

    Side effects:
        - Sends welcome message to user
        - Logs command execution with user ID
        - Creates reply keyboard for quick access to /cleanup command
    """

    logger.info("Command /start from user > %s", message.from_user.id)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Clear history")]], resize_keyboard=True
    )

    await message.answer(
        "FreelanceHunterBot – bot for search freelance tasks", reply_markup=kb
    )
