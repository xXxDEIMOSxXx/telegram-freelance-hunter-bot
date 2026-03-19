"""Unit tests for main application entry point"""

from unittest.mock import AsyncMock, patch

import pytest


class TestMainEntry:
    """Tests for main application entry point"""

    @pytest.mark.asyncio
    async def test_main_with_successful_bootstrap(self):
        """Test main function with successful bootstrap

        Verifies application starts when bootstrap succeeds
        """

        with (
            patch("src.main.bootstrap", new_callable=AsyncMock) as mock_bootstrap,
            patch("src.main.create_bot") as mock_create_bot,
            patch("src.main.create_telegram_client") as mock_create_client,
        ):
            mock_bootstrap.return_value = True
            mock_bot = AsyncMock()
            mock_dp = AsyncMock()
            mock_create_bot.return_value = (mock_bot, mock_dp)

            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_create_client.return_value = mock_client
            mock_dp.start_polling = AsyncMock()

            from src.main import main

            # Mock the polling to prevent infinite loop
            async def mock_polling(*args, **kwargs):
                raise KeyboardInterrupt()

            mock_dp.start_polling.side_effect = mock_polling

            try:
                await main()
            except KeyboardInterrupt:
                pass

            # Verify bootstrap was called
            mock_bootstrap.assert_called_once()
            # Verify bot was created
            mock_create_bot.assert_called_once()
            # Verify telegram client was created
            mock_create_client.assert_called_once()
            # Verify client started
            mock_client.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_with_failed_bootstrap(self):
        """Test main function when bootstrap fails

        Verifies application exits gracefully when bootstrap fails
        """

        with (
            patch("src.main.bootstrap", new_callable=AsyncMock) as mock_bootstrap,
            patch("src.main.create_bot") as mock_create_bot,
            patch("src.main.logger"),
        ):
            mock_bootstrap.return_value = False

            from src.main import main

            await main()

            # Verify bootstrap was called
            mock_bootstrap.assert_called_once()
            # Bot creation should not be called
            mock_create_bot.assert_not_called()

    @pytest.mark.asyncio
    async def test_main_creates_bot_with_correct_order(self):
        """Test main creates components in correct order

        Verifies: bootstrap -> bot -> client -> start
        """

        call_order = []

        async def track_bootstrap():
            call_order.append("bootstrap")
            return True

        def track_create_bot():
            call_order.append("create_bot")
            return AsyncMock(), AsyncMock()

        def track_create_client(bot):
            call_order.append("create_client")
            client = AsyncMock()
            client.start = AsyncMock(side_effect=KeyboardInterrupt())
            return client

        with (
            patch("src.main.bootstrap", side_effect=track_bootstrap),
            patch("src.main.create_bot", side_effect=track_create_bot),
            patch("src.main.create_telegram_client", side_effect=track_create_client),
            patch("src.main.logger"),
        ):
            from src.main import main

            try:
                await main()
            except KeyboardInterrupt:
                pass

            assert call_order == ["bootstrap", "create_bot", "create_client"]
