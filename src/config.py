from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # protection for extra variables in .env
    )

    # Telegram API (userbot — Telethon)
    API_ID: int
    API_HASH: str

    # Telegram Bot (aiogram)
    BOT_TOKEN: str
    BOT_CHAT_ID: int

    # PostgreSQL database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Data path
    DATA_DIR: Path = Field(default=Path("data"))
    KEYWORDS_FILE: Path
    BLACKLIST_FILE: Path
    KEYWORD_FORMS_CACHE: Path

    # Helper properties
    @property
    def keywords_path(self) -> Path:
        return Path(self.KEYWORDS_FILE)

    @property
    def blacklist_path(self) -> Path:
        return Path(self.BLACKLIST_FILE)

    @property
    def keyword_forms_path(self) -> Path:
        return Path(self.KEYWORD_FORMS_CACHE)

    @property
    def db_config(self) -> dict:
        return {
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "database": self.DB_NAME,
        }


settings = Settings()
