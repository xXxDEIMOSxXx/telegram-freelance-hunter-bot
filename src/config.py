"""Project configuration via .env and pydantic-settings"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env file using Pydantic.

    Manages configuration for:
    - Telegram API credentials (Telethon)
    - Telegram Bot credentials (aiogram)
    - PostgreSQL database connection
    - Data file paths

    Attributes:
        API_ID: Telegram API ID for Telethon client
        API_HASH: Telegram API hash for Telethon client
        BOT_TOKEN: Telegram bot token from BotFather
        BOT_CHAT_ID: Chat ID where bot forwards filtered messages
        LANG_CODE: Language code for bot user (e.g., 'en')
        SYSTEM_LANG_CODE: System language code (e.g., 'en-US')
        DB_HOST: PostgreSQL database host
        DB_PORT: PostgreSQL database port
        DB_USER: PostgreSQL database user
        DB_PASSWORD: PostgreSQL database password
        DB_NAME: PostgreSQL database name
        DATA_DIR: Directory for data files (default: 'data')
        CHATS_FILE: Path to chats configuration file
        KEYWORDS_FILE: Path to keywords configuration file
        BLACKLIST_FILE: Path to blacklist configuration file
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # protection for extra variables in .env
    )

    # Telegram API (userbot — Telethon)
    API_ID: int
    API_HASH: str

    # Telegram Bot (aiogram)
    BOT_TOKEN: str
    BOT_CHAT_ID: int
    LANG_CODE: str
    SYSTEM_LANG_CODE: str

    # PostgreSQL database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Data path
    DATA_DIR: Path = Field(default=Path("data"))
    CHATS_FILE: Path
    KEYWORDS_FILE: Path
    BLACKLIST_FILE: Path

    # Helper properties
    @property
    def channels_and_groups_path(self) -> Path:
        """Path to the channels and groups (chats) JSON file"""

        return self.CHATS_FILE

    @property
    def keywords_path(self) -> Path:
        """Path to the keywords JSON file"""

        return self.KEYWORDS_FILE

    @property
    def blacklist_path(self) -> Path:
        """Path to the blacklist JSON file"""

        return self.BLACKLIST_FILE

    @property
    def db_config(self) -> dict:
        """Returns a ready-made dictionary for connecting to the database"""

        return {
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "database": self.DB_NAME,
        }

    @property
    def db_url(self) -> str:
        """Async PostgreSQL URL for SQLAlchemy/asyncpg"""

        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
