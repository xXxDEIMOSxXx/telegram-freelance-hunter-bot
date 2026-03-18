"""PostgreSQL database models"""

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TelegramMessage(Base):  # pylint: disable=too-few-public-methods
    """Telegram messages history model"""

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
