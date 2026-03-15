"""PostgreSQL database models"""

from sqlalchemy import Boolean, Column, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TelegramMessage(Base):  # pylint: disable=too-few-public-methods
    """Telegram messages history model"""

    __tablename__ = "telegram_messages_history"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    message_datetime = Column(DateTime, nullable=False, default=func.now)
    have_keyword = Column(Boolean, nullable=False)
    keyword = Column(Text, nullable=False)
    group_or_channel = Column(Text, nullable=False)
    sender = Column(Text, nullable=False)
    message_text = Column(Text, nullable=False)
