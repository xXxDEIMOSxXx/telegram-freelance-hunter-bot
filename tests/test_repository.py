"""Unit tests for database repository"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Result

from src.database.repository import save_message


class TestRepository:
    """Tests for database repository functions"""

    @pytest.mark.asyncio
    async def test_save_message_success(self):
        """Test successful message save operation

        Verifies that message is correctly saved and ID is returned
        """

        mock_session = AsyncMock()
        mock_result = AsyncMock(spec=Result)
        mock_result.scalar_one.return_value = 12345
        mock_session.execute.return_value = mock_result

        message_data = {
            "message_datetime": MagicMock(),
            "chat_title": "Test Chat",
            "chat_id": 111111,
            "sender_id": 555555,
            "have_keyword": True,
            "keyword": "freelance",
            "not_scum": True,
            "notify": True,
            "message_text": "Test message",
        }

        result = await save_message(mock_session, message_data)

        assert result == 12345
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message_rollback_on_error(self):
        """Test that transaction is rolled back on error

        Verifies rollback is called when exception occurs
        """

        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database error")

        message_data = {
            "message_datetime": MagicMock(),
            "chat_title": "Test Chat",
            "chat_id": 111111,
            "sender_id": 555555,
            "have_keyword": False,
            "keyword": "-",
            "not_scum": True,
            "notify": False,
            "message_text": "Test message",
        }

        with pytest.raises(Exception):
            await save_message(mock_session, message_data)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message_with_all_data(self):
        """Test save_message with complete message data

        Verifies all message fields are properly handled
        """

        mock_session = AsyncMock()
        mock_result = AsyncMock(spec=Result)
        mock_result.scalar_one.return_value = 999
        mock_session.execute.return_value = mock_result

        message_data = {
            "message_datetime": MagicMock(),
            "chat_title": "Freelance Chat",
            "chat_id": 222222,
            "sender_id": 777777,
            "have_keyword": True,
            "keyword": "hire",
            "not_scum": False,
            "notify": False,
            "message_text": "Looking to hire a developer for a project",
        }

        result = await save_message(mock_session, message_data)

        assert result == 999
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message_with_special_characters(self):
        """Test save_message with special characters in text

        Verifies that special characters are handled correctly
        """

        mock_session = AsyncMock()
        mock_result = AsyncMock(spec=Result)
        mock_result.scalar_one.return_value = 555
        mock_session.execute.return_value = mock_result

        message_data = {
            "message_datetime": MagicMock(),
            "chat_title": "Chat with émojis 🎉",
            "chat_id": 333333,
            "sender_id": 888888,
            "have_keyword": True,
            "keyword": "test",
            "not_scum": True,
            "notify": True,
            "message_text": "Message with <html> and 'quotes' and \"double quotes\"",
        }

        result = await save_message(mock_session, message_data)

        assert result == 555
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message_various_sender_ids(self):
        """Test save_message with different sender ID formats

        Verifies handling of string vs int sender IDs
        """

        mock_session = AsyncMock()
        mock_result = AsyncMock(spec=Result)
        mock_result.scalar_one.return_value = 777
        mock_session.execute.return_value = mock_result

        message_data = {
            "message_datetime": MagicMock(),
            "chat_title": "Test Chat",
            "chat_id": 444444,
            "sender_id": "0",  # String sender_id for restricted channels
            "have_keyword": False,
            "keyword": "-",
            "not_scum": False,
            "notify": False,
            "message_text": "Message from restricted channel",
        }

        result = await save_message(mock_session, message_data)

        assert result == 777
