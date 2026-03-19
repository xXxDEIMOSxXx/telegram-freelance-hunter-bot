"""Unit tests for message processor service"""

from unittest.mock import AsyncMock, patch

import pytest

from src.services.message_processor import process_message


class TestMessageProcessor:
    """Tests for message processor service"""

    @pytest.mark.asyncio
    async def test_process_message_with_keyword_not_blacklisted(
        self, mock_telethon_event
    ):
        """Test message processing when keyword found and user not blacklisted

        Verifies that notification flag is set when conditions are met

        Args:
            mock_telethon_event: Pytest fixture providing mock message event
        """

        mock_session = AsyncMock()

        with (
            patch("src.services.message_processor.get_keywords") as mock_kw,
            patch("src.services.message_processor.get_blacklist") as mock_bl,
            patch(
                "src.services.message_processor.save_message", new_callable=AsyncMock
            ),
        ):
            mock_kw.find_keyword_in_message_text.return_value = (True, "freelance")
            mock_bl.is_blacklisted.return_value = False

            result = await process_message(
                mock_telethon_event, "https://t.me/freelance", mock_session
            )

            assert result["notify"] is True
            assert result["keyword"] == "freelance"
            assert "text" in result
            assert "chat_title" in result
            assert "chat_link" in result

    @pytest.mark.asyncio
    async def test_process_message_with_keyword_blacklisted(self, mock_telethon_event):
        """Test message processing when keyword found but user is blacklisted

        Verifies that notification is not sent for blacklisted users

        Args:
            mock_telethon_event: Pytest fixture providing mock message event
        """

        mock_session = AsyncMock()

        with (
            patch("src.services.message_processor.get_keywords") as mock_kw,
            patch("src.services.message_processor.get_blacklist") as mock_bl,
            patch(
                "src.services.message_processor.save_message", new_callable=AsyncMock
            ),
        ):
            mock_kw.find_keyword_in_message_text.return_value = (True, "freelance")
            mock_bl.is_blacklisted.return_value = True

            result = await process_message(
                mock_telethon_event, "https://t.me/freelance", mock_session
            )

            assert result["notify"] is False

    @pytest.mark.asyncio
    async def test_process_message_no_keyword(self, mock_telethon_event):
        """Test message processing when no keyword found

        Verifies that no notification is sent without keywords

        Args:
            mock_telethon_event: Pytest fixture providing mock message event
        """

        mock_session = AsyncMock()

        with (
            patch("src.services.message_processor.get_keywords") as mock_kw,
            patch("src.services.message_processor.get_blacklist") as mock_bl,
            patch(
                "src.services.message_processor.save_message", new_callable=AsyncMock
            ),
        ):
            mock_kw.find_keyword_in_message_text.return_value = (False, "-")
            mock_bl.is_blacklisted.return_value = False

            result = await process_message(
                mock_telethon_event, "https://t.me/freelance", mock_session
            )

            assert result["notify"] is False

    @pytest.mark.asyncio
    async def test_process_message_null_sender_id(self, mock_telethon_event):
        """Test message processing when sender_id is None

        Verifies that None sender_id defaults to 0

        Args:
            mock_telethon_event: Pytest fixture providing mock message event
        """

        mock_telethon_event.sender_id = None
        mock_session = AsyncMock()

        with (
            patch("src.services.message_processor.get_keywords") as mock_kw,
            patch("src.services.message_processor.get_blacklist") as mock_bl,
            patch(
                "src.services.message_processor.save_message", new_callable=AsyncMock
            ),
        ):
            mock_kw.find_keyword_in_message_text.return_value = (False, "-")
            mock_bl.is_blacklisted.return_value = False

            result = await process_message(
                mock_telethon_event, "https://t.me/freelance", mock_session
            )

            # Should not raise exception
            assert "notify" in result

    @pytest.mark.asyncio
    async def test_process_message_saves_to_database(self, mock_telethon_event):
        """Test that message is saved to database

        Verifies that save_message is called with correct data

        Args:
            mock_telethon_event: Pytest fixture providing mock message event
        """

        mock_session = AsyncMock()

        with (
            patch("src.services.message_processor.get_keywords") as mock_kw,
            patch("src.services.message_processor.get_blacklist") as mock_bl,
            patch(
                "src.services.message_processor.save_message", new_callable=AsyncMock
            ) as mock_save,
        ):
            mock_kw.find_keyword_in_message_text.return_value = (False, "-")
            mock_bl.is_blacklisted.return_value = False

            await process_message(
                mock_telethon_event, "https://t.me/freelance", mock_session
            )

            # Verify save_message was called
            mock_save.assert_called_once()

            # Verify message data was passed
            call_args = mock_save.call_args
            assert "message_data" in call_args.kwargs
            assert "session" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_process_message_empty_text(self, mock_telethon_event):
        """Test message processing with empty message text

        Verifies graceful handling of empty messages

        Args:
            mock_telethon_event: Pytest fixture providing mock message event
        """

        mock_telethon_event.raw_text = ""
        mock_session = AsyncMock()

        with (
            patch("src.services.message_processor.get_keywords") as mock_kw,
            patch("src.services.message_processor.get_blacklist") as mock_bl,
            patch(
                "src.services.message_processor.save_message", new_callable=AsyncMock
            ),
        ):
            mock_kw.find_keyword_in_message_text.return_value = (False, "-")
            mock_bl.is_blacklisted.return_value = False

            result = await process_message(
                mock_telethon_event, "https://t.me/freelance", mock_session
            )

            assert result["notify"] is False
