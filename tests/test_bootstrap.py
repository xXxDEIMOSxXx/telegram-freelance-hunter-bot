"""Unit tests for bootstrap module"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bootstrap import bootstrap


class TestBootstrap:
    """Tests for application bootstrap initialization"""

    @pytest.mark.asyncio
    async def test_bootstrap_success(self):
        """Test successful bootstrap initialization

        Verifies all bootstrap steps complete successfully
        """

        with (
            patch(
                "src.bootstrap.check_telegram_api_connection", new_callable=AsyncMock
            ) as mock_api,
            patch("src.bootstrap.init_database", new_callable=AsyncMock) as mock_db,
            patch("src.bootstrap.get_keywords") as mock_kw,
            patch("src.bootstrap.get_blacklist") as mock_bl,
            patch("src.bootstrap.logger"),
        ):
            mock_kw.preload = MagicMock()
            mock_bl.preload = MagicMock()

            result = await bootstrap()

            assert result is True
            mock_api.assert_called_once()
            mock_db.assert_called_once()
            mock_kw.preload.assert_called_once()
            mock_bl.preload.assert_called_once()

    @pytest.mark.asyncio
    async def test_bootstrap_api_check_fails(self):
        """Test bootstrap when API check fails

        Verifies bootstrap fails gracefully when API is unreachable
        """

        with (
            patch(
                "src.bootstrap.check_telegram_api_connection", new_callable=AsyncMock
            ) as mock_api,
            patch("src.bootstrap.init_database", new_callable=AsyncMock),
        ):
            mock_api.side_effect = Exception("API unreachable")

            result = await bootstrap()

            assert result is False

    @pytest.mark.asyncio
    async def test_bootstrap_database_init_fails(self):
        """Test bootstrap when database initialization fails

        Verifies bootstrap fails when database connection fails
        """

        with (
            patch(
                "src.bootstrap.check_telegram_api_connection", new_callable=AsyncMock
            ),
            patch("src.bootstrap.init_database", new_callable=AsyncMock) as mock_db,
        ):
            mock_db.side_effect = Exception("Database connection failed")

            result = await bootstrap()

            assert result is False

    @pytest.mark.asyncio
    async def test_bootstrap_keyword_loading_fails(self):
        """Test bootstrap when keyword preloading fails

        Verifies bootstrap handles keyword loading errors
        """

        with (
            patch(
                "src.bootstrap.check_telegram_api_connection", new_callable=AsyncMock
            ),
            patch("src.bootstrap.init_database", new_callable=AsyncMock),
            patch("src.bootstrap.get_keywords") as mock_kw,
            patch("src.bootstrap.get_blacklist"),
        ):
            mock_kw.preload.side_effect = Exception("Keyword loading failed")

            result = await bootstrap()

            assert result is False

    @pytest.mark.asyncio
    async def test_bootstrap_blacklist_loading_fails(self):
        """Test bootstrap when blacklist preloading fails

        Verifies bootstrap handles blacklist loading errors
        """

        with (
            patch(
                "src.bootstrap.check_telegram_api_connection", new_callable=AsyncMock
            ),
            patch("src.bootstrap.init_database", new_callable=AsyncMock),
            patch("src.bootstrap.get_keywords") as mock_kw,
            patch("src.bootstrap.get_blacklist") as mock_bl,
        ):
            mock_kw.preload = lambda: None
            mock_bl.preload.side_effect = Exception("Blacklist loading failed")

            result = await bootstrap()

            assert result is False

    @pytest.mark.asyncio
    async def test_bootstrap_sequence(self):
        """Test bootstrap execution sequence

        Verifies steps are called in correct order
        """

        call_order = []

        async def track_api():
            call_order.append("api")

        async def track_db():
            call_order.append("db")

        def track_kw():
            call_order.append("kw")

        def track_bl():
            call_order.append("bl")

        with (
            patch("src.bootstrap.check_telegram_api_connection", side_effect=track_api),
            patch("src.bootstrap.init_database", side_effect=track_db),
            patch("src.bootstrap.get_keywords") as mock_kw,
            patch("src.bootstrap.get_blacklist") as mock_bl,
        ):
            mock_kw.preload = track_kw
            mock_bl.preload = track_bl

            await bootstrap()

            # Verify order: API -> DB -> Keywords -> Blacklist
            assert call_order == ["api", "db", "kw", "bl"]
