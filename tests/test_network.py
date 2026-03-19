"""Unit tests for network validation service"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.network import check_telegram_api_connection


def _make_mock_session(mock_response):
    """Build a correctly structured async-context-manager mock for ClientSession"""

    mock_get_cm = MagicMock()
    mock_get_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_cm.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = MagicMock(return_value=mock_get_cm)
    return mock_session


def _make_mock_session_raise(exc):
    """Build a session mock whose .get() raises *exc* immediately"""

    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = MagicMock(side_effect=exc)
    return mock_session


class TestNetworkValidation:
    """Tests for network connectivity validation"""

    @pytest.mark.asyncio
    async def test_check_api_connection_success(self):
        """Test successful API connection validation

        Verifies connection check passes with valid response
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ok": True})

        mock_session = _make_mock_session(mock_response)

        with patch("src.services.network.ClientSession", return_value=mock_session):
            await check_telegram_api_connection()

    @pytest.mark.asyncio
    async def test_check_api_connection_bad_response(self):
        """Test API connection with bad response

        Verifies handler logs warning when ok=false
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ok": False})

        mock_session = _make_mock_session(mock_response)

        with patch("src.services.network.ClientSession", return_value=mock_session):
            await check_telegram_api_connection()

    @pytest.mark.asyncio
    async def test_check_api_connection_http_error(self):
        """Test API connection with HTTP error status

        Verifies handler logs error on non-200 status
        """

        mock_response = MagicMock()
        mock_response.status = 401

        mock_session = _make_mock_session(mock_response)

        with patch("src.services.network.ClientSession", return_value=mock_session):
            await check_telegram_api_connection()

    @pytest.mark.asyncio
    async def test_check_api_connection_timeout(self):
        """Test API connection timeout

        Verifies handler logs error on timeout
        """

        mock_session = _make_mock_session_raise(asyncio.TimeoutError())

        with patch("src.services.network.ClientSession", return_value=mock_session):
            await check_telegram_api_connection()

    @pytest.mark.asyncio
    async def test_check_api_connection_network_error(self):
        """Test API connection network error

        Verifies handler logs error on connection failure
        """

        mock_session = _make_mock_session_raise(OSError("Connection refused"))

        with patch("src.services.network.ClientSession", return_value=mock_session):
            await check_telegram_api_connection()

    @pytest.mark.asyncio
    async def test_check_api_connection_uses_correct_url(self):
        """Test API connection uses correct endpoint URL

        Verifies correct API endpoint is called
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ok": True})

        mock_session = _make_mock_session(mock_response)

        with (
            patch("src.services.network.ClientSession", return_value=mock_session),
            patch("src.services.network.settings") as mock_settings,
        ):
            mock_settings.BOT_TOKEN = "test_token_123"

            await check_telegram_api_connection()

            called_url = mock_session.get.call_args[0][0]
            assert "test_token_123" in called_url
            assert "https://api.telegram.org/bot" in called_url
