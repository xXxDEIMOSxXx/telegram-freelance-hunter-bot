"""Unit tests for bot handlers"""

from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from src.bot.handlers.cleanup import cmd_cleanup
from src.bot.handlers.start import cmd_start


class TestStartHandler:
    """Tests for /start command handler"""

    @pytest.mark.asyncio
    async def test_start_command_sends_message(self):
        """Test that /start command sends welcome message

        Verifies correct message is sent to user
        """
        mock_message = AsyncMock()
        mock_message.from_user.id = 12345

        await cmd_start(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "FreelanceHunterBot" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_start_command_sends_keyboard(self):
        """Test that /start command includes reply keyboard

        Verifies keyboard is sent with message
        """
        mock_message = AsyncMock()
        mock_message.from_user.id = 12345

        await cmd_start(mock_message)

        call_kwargs = mock_message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs

    @pytest.mark.asyncio
    async def test_start_command_with_different_users(self):
        """Test /start command with different user IDs

        Verifies handler works for multiple users
        """

        for user_id in [111, 222, 333]:
            mock_message = AsyncMock()
            mock_message.from_user.id = user_id

            await cmd_start(mock_message)

            mock_message.answer.assert_called_once()


class TestCleanupHandler:
    """Tests for cleanup/clear history handler"""

    @pytest.mark.asyncio
    async def test_cleanup_handler_deletes_messages(self):
        """Test cleanup handler attempts to delete messages

        Verifies delete_message is called
        """

        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 67890
        mock_message.message_id = 100
        mock_message.bot = AsyncMock()
        mock_message.bot.delete_message = AsyncMock()

        await cmd_cleanup(mock_message)

        # Should have attempted to delete at least one message
        assert mock_message.bot.delete_message.call_count > 0

    @pytest.mark.asyncio
    async def test_cleanup_handler_respects_max_attempts(self):
        """Test cleanup doesn't exceed maximum delete attempts

        Verifies MAX_DELETE_ATTEMPTS limit is respected
        """

        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 67890
        mock_message.message_id = 100
        mock_message.bot = AsyncMock()
        mock_message.bot.delete_message = AsyncMock()

        await cmd_cleanup(mock_message)

        # Should not exceed MAX_DELETE_ATTEMPTS (50)
        assert mock_message.bot.delete_message.call_count <= 50

    @pytest.mark.asyncio
    async def test_cleanup_handler_skips_missing_messages(self):
        """Test cleanup handles missing messages gracefully

        Verifies handler continues after "message not found" error
        """

        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 67890
        mock_message.message_id = 100
        mock_message.bot = AsyncMock()

        # First call raises "message to delete not found"
        error = TelegramBadRequest(400, "message to delete not found")
        mock_message.bot.delete_message.side_effect = error

        # Should not raise exception
        await cmd_cleanup(mock_message)

        # Should send response message
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_handler_stops_on_old_messages(self):
        """Test cleanup stops when encountering too-old messages

        Verifies handler stops on "can't delete message" error
        """

        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 67890
        mock_message.message_id = 100
        mock_message.bot = AsyncMock()

        # Raise "can't delete message" error (for old messages)
        error = TelegramBadRequest(400, "can't delete message")
        mock_message.bot.delete_message.side_effect = error

        await cmd_cleanup(mock_message)

        # Should have been called only once (stops on this error)
        assert mock_message.bot.delete_message.call_count == 1

    @pytest.mark.asyncio
    async def test_cleanup_handler_sends_status_message(self):
        """Test cleanup sends status message after completion

        Verifies user receives confirmation message
        """

        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 67890
        mock_message.message_id = 100
        mock_message.bot = AsyncMock()
        mock_message.bot.delete_message = AsyncMock(
            side_effect=TelegramBadRequest(400, "not found")
        )

        await cmd_cleanup(mock_message)

        # Should send answer with deleted count
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Deleted" in call_args

    @pytest.mark.asyncio
    async def test_cleanup_handler_error_handling(self):
        """Test cleanup handles unexpected errors gracefully

        Verifies exception doesn't crash handler
        """

        mock_message = AsyncMock()
        mock_message.from_user.id = 12345
        mock_message.chat.id = 67890
        mock_message.message_id = 100
        mock_message.bot = AsyncMock()
        mock_message.bot.delete_message = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        # Should not raise exception
        await cmd_cleanup(mock_message)

        # Should send error message
        mock_message.answer.assert_called()
