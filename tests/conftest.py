"""Pytest configuration and shared fixtures for tests"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_settings():
    """Mock Settings object for testing

    Returns:
        Settings: Mock settings with test values
    """

    with patch("src.config.settings") as mock:
        mock.API_ID = 12345
        mock.API_HASH = "test_hash"
        mock.BOT_TOKEN = "test_token"
        mock.BOT_CHAT_ID = 67890
        mock.LANG_CODE = "en"
        mock.SYSTEM_LANG_CODE = "en-US"
        mock.DB_HOST = "localhost"
        mock.DB_PORT = 5432
        mock.DB_USER = "test_user"
        mock.DB_PASSWORD = "test_pass"
        mock.DB_NAME = "test_db"
        mock.DATA_DIR = Path("data")
        mock.CHATS_FILE = Path("data/chats.json")
        mock.KEYWORDS_FILE = Path("data/keywords.json")
        mock.BLACKLIST_FILE = Path("data/blacklist.json")
        yield mock


@pytest.fixture
def mock_keywords_file(tmp_path):
    """Create a mock keywords.json file for testing

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path: Path to the mock keywords file
    """

    keywords_data = {
        "categories": {
            "freelance": {
                "keywords": [
                    {"term": "freelance"},
                    {"term": "hire"},
                    {"term": "project"},
                ]
            },
            "coursework": {
                "keywords": [
                    {"term": "homework"},
                    {"term": "assignment"},
                    {"term": "essay"},
                ]
            },
        }
    }

    keywords_file = tmp_path / "keywords.json"
    keywords_file.write_text(json.dumps(keywords_data), encoding="utf-8")
    return keywords_file


@pytest.fixture
def mock_blacklist_file(tmp_path):
    """Create a mock blacklist.json file for testing

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path: Path to the mock blacklist file
    """

    blacklist_data = [{"user_id": 111111}, {"user_id": 222222}, {"user_id": 333333}]
    blacklist_file = tmp_path / "blacklist.json"
    blacklist_file.write_text(json.dumps(blacklist_data), encoding="utf-8")
    return blacklist_file


@pytest.fixture
def mock_chats_file(tmp_path):
    """Create a mock chats.json file for testing

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path: Path to the mock chats file
    """

    chats_data = [
        {"chat_id": 111111, "title": "Freelance Chat", "url": "https://t.me/freelance"},
        {"chat_id": 222222, "title": "Homework Chat", "url": "https://t.me/homework"},
    ]
    chats_file = tmp_path / "chats.json"
    chats_file.write_text(json.dumps(chats_data), encoding="utf-8")
    return chats_file


@pytest.fixture
async def mock_async_session():
    """Mock AsyncSession for database testing

    Returns:
        AsyncMock: Mock async database session
    """

    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.begin = AsyncMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=None),
            __aexit__=AsyncMock(return_value=None),
        )
    )
    return session


@pytest.fixture
def mock_telethon_event():
    """Create a mock Telethon message event

    Returns:
        MagicMock: Mock NewMessage event
    """

    event = MagicMock()
    event.chat_id = 111111
    event.id = 123456
    event.raw_text = "I need to hire someone for a freelance python project"
    event.sender_id = 555555
    event.chat = MagicMock()
    event.chat.id = 111111
    event.chat.title = "Freelance Chat"
    return event


@pytest.fixture
def mock_aiogram_bot():
    """Create a mock aiogram Bot instance

    Returns:
        AsyncMock: Mock Bot instance
    """

    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.delete_message = AsyncMock()
    return bot


@pytest.fixture
def mock_logger():
    """Mock logger for testing

    Returns:
        MagicMock: Mock logger instance
    """

    logger = MagicMock()
    logger.info = MagicMock()
    logger.success = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    logger.critical = MagicMock()
    return logger
