"""PostgreSQL database models"""

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TelegramMessage(Base):  # pylint: disable=too-few-public-methods
    """
    SQLAlchemy ORM model for Telegram messages history

    Stores metadata and content of messages processed by the bot including:
    - Message identifiers and timestamps
    - Chat and sender information
    - Keyword detection results
    - Spam/scam detection (blacklist status)
    - Notification flags

    Attributes:
        message_id: Primary key, auto-incremented message identifier
        message_datetime: UTC timestamp when message was received (auto-set)
        chat_title: Title of the Telegram chat/channel
        chat_id: Unique Telegram chat identifier
        sender_id: Telegram user ID of message sender
        have_keyword: Boolean flag indicating if message contains keywords
        keyword: Matched keyword (or "-" if none found)
        not_scum: Boolean flag for user blacklist status (False = blacklisted)
        notify: Boolean flag to trigger bot notification (keyword found AND not blacklisted)
        message_text: Full text content of the message

    Table name: telegram_bot_messages_history
    """

    # ToDo for future: in case of expanding/complicating the structure,  # pylint: disable=fixme
    #  divide the general table into subtables: users, chats, history, etc.
    #  Also add indexes - if database continue to growing

    __tablename__ = "telegram_bot_messages_history"

    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_datetime = Column(DateTime(timezone=True), nullable=False, default=func.now)
    chat_title = Column(Text, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    sender_id = Column(BigInteger, nullable=False)
    have_keyword = Column(Boolean, nullable=False, default=False)
    keyword = Column(Text, nullable=False, default="-")
    not_scum = Column(Boolean, nullable=False, default=False)
    notify = Column(Boolean, nullable=False, default=False)
    message_text = Column(Text, nullable=False, default="-")

    def __repr__(self):
        return (
            f"<TelegramMessage(id={self.message_id}, keyword='{self.keyword[:30]}...')>"
        )
