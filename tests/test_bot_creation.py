"""Unit tests for bot creation and initialization"""

from unittest.mock import MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher

from src.bot.bot import create_bot


class TestBotCreation:
    """Tests for bot creation and initialization"""

    def test_create_bot_success(self):
        """Test successful bot creation

        Verifies bot and dispatcher are created correctly
        """

        with (
            patch("src.bot.bot.Bot") as mock_bot_class,
            patch("src.bot.bot.Dispatcher") as mock_dp_class,
            patch("src.bot.bot.settings") as mock_settings,
        ):
            mock_settings.BOT_TOKEN = "test_token"
            mock_bot_instance = MagicMock(spec=Bot)
            mock_dp_instance = MagicMock(spec=Dispatcher)
            mock_bot_class.return_value = mock_bot_instance
            mock_dp_class.return_value = mock_dp_instance

            bot, dp = create_bot()

            assert bot == mock_bot_instance
            assert dp == mock_dp_instance
            mock_bot_class.assert_called_once_with(token="test_token")
            mock_dp_class.assert_called_once()

    def test_create_bot_includes_routers(self):
        """Test that bot includes all required routers

        Verifies start and cleanup routers are registered
        """

        with (
            patch("src.bot.bot.Bot"),
            patch("src.bot.bot.Dispatcher") as mock_dp_class,
            patch("src.bot.bot.settings"),
        ):
            mock_dp_instance = MagicMock(spec=Dispatcher)
            mock_dp_class.return_value = mock_dp_instance

            bot, dp = create_bot()

            # Verify include_router was called (at least twice for start and cleanup)
            assert mock_dp_instance.include_router.call_count >= 2

    def test_create_bot_initialization_error(self):
        """Test bot creation failure

        Verifies exception is raised when bot creation fails
        """

        with patch("src.bot.bot.Bot") as mock_bot_class, patch("src.bot.bot.settings"):
            mock_bot_class.side_effect = Exception("Invalid token")

            with pytest.raises(Exception):
                create_bot()

    def test_create_bot_returns_tuple(self):
        """Test that create_bot returns tuple of (Bot, Dispatcher)

        Verifies return type is correct
        """

        with (
            patch("src.bot.bot.Bot"),
            patch("src.bot.bot.Dispatcher"),
            patch("src.bot.bot.settings"),
        ):
            result = create_bot()

            assert isinstance(result, tuple)
            assert len(result) == 2
