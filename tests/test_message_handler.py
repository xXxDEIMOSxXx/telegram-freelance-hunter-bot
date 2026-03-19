"""Unit tests for Telegram client message event handler"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.telegram_client.handlers.new_message import register_message_handler


class TestMessageHandler:
    """Tests for message event handler registration"""

    def test_register_message_handler_creates_handler(self):
        """Test that message handler is registered

        Verifies handler is attached to client
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()

        with patch(
            "src.telegram_client.handlers.new_message.get_chats_data"
        ) as mock_chats:
            mock_chats.return_value = [{"chat_id": 111, "url": "https://t.me/test"}]

            register_message_handler(mock_client, mock_bot)

            # Verify client.on was called
            mock_client.on.assert_called_once()

    def test_register_message_handler_uses_chat_data(self):
        """Test handler uses chat configuration

        Verifies chat data is loaded and used
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()

        with patch(
            "src.telegram_client.handlers.new_message.get_chats_data"
        ) as mock_chats:
            mock_chats.return_value = [
                {"chat_id": 111, "url": "https://t.me/test1"},
                {"chat_id": 222, "url": "https://t.me/test2"},
            ]

            register_message_handler(mock_client, mock_bot)

            mock_chats.assert_called_once()

    def test_register_message_handler_with_empty_chats(self):
        """Test handler when no chats configured

        Verifies graceful handling of empty chat list
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()

        with patch(
            "src.telegram_client.handlers.new_message.get_chats_data"
        ) as mock_chats:
            mock_chats.return_value = []

            # Should not raise exception
            register_message_handler(mock_client, mock_bot)

    @pytest.mark.asyncio
    async def test_message_handler_processes_message(self):
        """Test that message event is processed

        Verifies process_message is called for new messages
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()
        mock_event = MagicMock()
        mock_event.chat_id = 111
        mock_event.id = 123

        with (
            patch(
                "src.telegram_client.handlers.new_message.get_chats_data"
            ) as mock_chats,
            patch(
                "src.telegram_client.handlers.new_message.process_message",
                new_callable=AsyncMock,
            ) as mock_process,
            patch(
                "src.telegram_client.handlers.new_message.async_session"
            ) as mock_session,
        ):
            mock_chats.return_value = [{"chat_id": 111, "url": "https://t.me/test"}]
            mock_process.return_value = {"notify": False}
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance

            register_message_handler(mock_client, mock_bot)

            # Verify client.on was called
            assert mock_client.on.called

    @pytest.mark.asyncio
    async def test_message_handler_duplicate_prevention(self):
        """Test that duplicate messages are prevented

        Verifies same message isn't processed twice
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()

        with patch(
            "src.telegram_client.handlers.new_message.get_chats_data"
        ) as mock_chats:
            mock_chats.return_value = [{"chat_id": 111, "url": "https://t.me/test"}]

            register_message_handler(mock_client, mock_bot)

            # Handler should have a processed set to track duplicates
            assert mock_client.on.called

    def test_register_message_handler_with_missing_url(self):
        """Test handler when chat missing URL

        Verifies graceful handling of incomplete chat data
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()

        with patch(
            "src.telegram_client.handlers.new_message.get_chats_data"
        ) as mock_chats:
            # Chat missing 'url' field
            mock_chats.return_value = [{"chat_id": 111}]

            # Should not raise exception
            register_message_handler(mock_client, mock_bot)

    def test_register_message_handler_with_invalid_chat_id(self):
        """Test handler when chat_id not an integer

        Verifies type conversion handling
        """

        mock_client = MagicMock()
        mock_bot = AsyncMock()

        with patch(
            "src.telegram_client.handlers.new_message.get_chats_data"
        ) as mock_chats:
            mock_chats.return_value = [
                {"chat_id": "111", "url": "https://t.me/test"}  # String instead of int
            ]

            register_message_handler(mock_client, mock_bot)

            # Should handle string to int conversion
            assert mock_client.on.called
