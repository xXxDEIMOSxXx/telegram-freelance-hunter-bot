"""Unit tests for Telegram client creation"""

from unittest.mock import MagicMock, patch

from telethon import TelegramClient

from src.telegram_client.client import create_telegram_client


class TestTelegramClientCreation:
    """Tests for Telegram client creation and setup"""

    def test_create_telegram_client_success(self):
        """Test successful Telegram client creation

        Verifies client is created with correct parameters
        """

        mock_bot = MagicMock()

        with (
            patch("src.telegram_client.client.TelegramClient") as mock_client_class,
            patch("src.telegram_client.client.register_message_handler"),
            patch("src.telegram_client.client.settings") as mock_settings,
        ):
            mock_settings.API_ID = 12345
            mock_settings.API_HASH = "test_hash"
            mock_settings.LANG_CODE = "en"
            mock_settings.SYSTEM_LANG_CODE = "en-US"

            mock_client_instance = MagicMock(spec=TelegramClient)
            mock_client_class.return_value = mock_client_instance

            result = create_telegram_client(mock_bot)

            assert result == mock_client_instance
            mock_client_class.assert_called_once()

    def test_create_telegram_client_uses_correct_credentials(self):
        """Test client creation uses correct credentials

        Verifies API credentials are passed correctly
        """

        mock_bot = MagicMock()

        with (
            patch("src.telegram_client.client.TelegramClient") as mock_client_class,
            patch("src.telegram_client.client.register_message_handler"),
            patch("src.telegram_client.client.settings") as mock_settings,
        ):
            mock_settings.API_ID = 99999
            mock_settings.API_HASH = "secret_hash"
            mock_settings.LANG_CODE = "uk"
            mock_settings.SYSTEM_LANG_CODE = "uk-UA"

            create_telegram_client(mock_bot)

            call_kwargs = mock_client_class.call_args.kwargs
            assert call_kwargs["api_id"] == 99999
            assert call_kwargs["api_hash"] == "secret_hash"

    def test_create_telegram_client_registers_handler(self):
        """Test that message handler is registered

        Verifies register_message_handler is called with client and bot
        """

        mock_bot = MagicMock()

        with (
            patch("src.telegram_client.client.TelegramClient"),
            patch(
                "src.telegram_client.client.register_message_handler"
            ) as mock_register,
            patch("src.telegram_client.client.settings"),
        ):
            create_telegram_client(mock_bot)

            mock_register.assert_called_once()
            call_args = mock_register.call_args[0]
            assert call_args[1] == mock_bot

    def test_create_telegram_client_connection_settings(self):
        """Test client creation uses connection retry settings

        Verifies connection retry parameters are set
        """

        mock_bot = MagicMock()

        with (
            patch("src.telegram_client.client.TelegramClient") as mock_client_class,
            patch("src.telegram_client.client.register_message_handler"),
            patch("src.telegram_client.client.settings"),
        ):
            create_telegram_client(mock_bot)

            call_kwargs = mock_client_class.call_args.kwargs
            assert "connection_retries" in call_kwargs
            assert "retry_delay" in call_kwargs
            assert call_kwargs["connection_retries"] == 360
            assert call_kwargs["retry_delay"] == 10

    def test_create_telegram_client_returns_client(self):
        """Test that function returns TelegramClient instance

        Verifies return type is TelegramClient
        """

        mock_bot = MagicMock()

        with (
            patch("src.telegram_client.client.TelegramClient") as mock_client_class,
            patch("src.telegram_client.client.register_message_handler"),
            patch("src.telegram_client.client.settings"),
        ):
            mock_client_instance = MagicMock(spec=TelegramClient)
            mock_client_class.return_value = mock_client_instance

            result = create_telegram_client(mock_bot)

            assert isinstance(result, MagicMock)
            assert result == mock_client_instance
