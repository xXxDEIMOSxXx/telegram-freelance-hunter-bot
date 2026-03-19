"""Unit tests for chats service"""

from pathlib import Path
from unittest.mock import patch

from src.services.chats import get_chats_data


class TestChatsService:
    """Tests for chats service functions"""

    def test_get_chats_data_valid_file(self, mock_chats_file):
        """Test get_chats_data with valid chats file

        Args:
            mock_chats_file: Pytest fixture providing mock chats file
        """

        with patch("src.services.chats.settings") as mock_settings:
            mock_settings.CHATS_FILE = mock_chats_file

            data = get_chats_data()

            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["chat_id"] == 111111
            assert data[1]["chat_id"] == 222222

    def test_get_chats_data_file_not_found(self):
        """Test get_chats_data when file doesn't exist

        Verifies graceful handling of missing file
        """

        with patch("src.services.chats.settings") as mock_settings:
            mock_settings.CHATS_FILE = Path("/nonexistent/path/chats.json")

            data = get_chats_data()

            assert data == []

    def test_get_chats_data_invalid_json(self, tmp_path):
        """Test get_chats_data with invalid JSON file

        Args:
            tmp_path: Pytest temporary directory fixture
        """

        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }", encoding="utf-8")

        with patch("src.services.chats.settings") as mock_settings:
            mock_settings.CHATS_FILE = invalid_file

            data = get_chats_data()

            assert data == []

    def test_get_chats_data_empty_file(self, tmp_path):
        """Test get_chats_data with empty JSON array

        Args:
            tmp_path: Pytest temporary directory fixture
        """

        empty_file = tmp_path / "chats.json"
        empty_file.write_text("[]", encoding="utf-8")

        with patch("src.services.chats.settings") as mock_settings:
            mock_settings.CHATS_FILE = empty_file

            data = get_chats_data()

            assert data == []

    def test_get_chats_data_structure(self, mock_chats_file):
        """Test get_chats_data returns correct structure

        Args:
            mock_chats_file: Pytest fixture providing mock chats file
        """

        with patch("src.services.chats.settings") as mock_settings:
            mock_settings.CHATS_FILE = mock_chats_file

            data = get_chats_data()

            # Verify structure of first chat entry
            assert "chat_id" in data[0]
            assert "title" in data[0]
            assert "url" in data[0]

            assert isinstance(data[0]["chat_id"], int)
            assert isinstance(data[0]["title"], str)
            assert isinstance(data[0]["url"], str)
