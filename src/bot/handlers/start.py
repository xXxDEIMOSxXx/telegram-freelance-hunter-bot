"""Bot start func"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.utils.logger import logger

router = Router()

# ToDo make nice inline keyboard, change start message  # pylint: disable=fixme


@router.message(Command("start"))
async def cmd_start(message: Message):
    """/start command"""

    logger.info(f"Command /start from user > {message.from_user.id}")

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Clear history")]], resize_keyboard=True
    )

    await message.answer(
        "FreelanceHunterBot – bot for search freelance tasks", reply_markup=kb
    )
