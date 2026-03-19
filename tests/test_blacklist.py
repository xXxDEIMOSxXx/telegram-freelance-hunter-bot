"""Unit tests for blacklist service"""

from pathlib import Path
from unittest.mock import patch

from src.services.blacklist import BlacklistService


class TestBlacklistService:
    """Tests for BlacklistService class"""

    def test_init(self):
        """Test BlacklistService initialization

        Verifies that _cache is None on initialization
        """

        service = BlacklistService()
        assert service._cache is None

    def test_is_blacklisted_empty_cache(self, mock_blacklist_file):
        """Test is_blacklisted with empty cache triggers lazy load

        Args:
            mock_blacklist_file: Pytest fixture providing mock blacklist file
        """

        service = BlacklistService()
        assert service._cache is None

        # Patch settings to use mock file
        with patch("src.services.blacklist.settings") as mock_settings:
            mock_settings.BLACKLIST_FILE = mock_blacklist_file

            # This should trigger lazy load
            result = service.is_blacklisted(111111)

            # Cache should be populated
            assert result is not None
            assert service._cache is not None
            assert isinstance(service._cache, set)

    def test_is_blacklisted_user_found(self, mock_blacklist_file):
        """Test is_blacklisted returns True for blacklisted user

        Args:
            mock_blacklist_file: Pytest fixture providing mock blacklist file
        """

        service = BlacklistService()
        service._cache = {111111, 222222, 333333}

        assert service.is_blacklisted(111111) is True
        assert service.is_blacklisted(222222) is True

    def test_is_blacklisted_user_not_found(self):
        """Test is_blacklisted returns False for non-blacklisted user

        Verifies that users not in blacklist return False
        """

        service = BlacklistService()
        service._cache = {111111, 222222, 333333}

        assert service.is_blacklisted(999999) is False
        assert service.is_blacklisted(123456) is False

    def test_is_blacklisted_empty_set(self):
        """Test is_blacklisted with empty blacklist set

        Verifies that empty blacklist returns False for all users
        """

        service = BlacklistService()
        service._cache = set()

        assert service.is_blacklisted(111111) is False
        assert service.is_blacklisted(999999) is False

    def test_load_blacklist_file_not_found(self):
        """Test _load when blacklist file doesn't exist

        Verifies graceful handling when file is missing
        """

        service = BlacklistService()

        with patch("src.services.blacklist.settings") as mock_settings:
            mock_settings.BLACKLIST_FILE = Path("/nonexistent/path/blacklist.json")

            service._load()

            # Should create empty set
            assert service._cache == set()

    def test_load_blacklist_invalid_json(self, tmp_path):
        """Test _load with invalid JSON file

        Args:
            tmp_path: Pytest temporary directory fixture
        """

        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }", encoding="utf-8")

        service = BlacklistService()

        with patch("src.services.blacklist.settings") as mock_settings:
            mock_settings.BLACKLIST_FILE = invalid_file

            # Should not raise exception
            service._load()

            # Should create empty set on error
            assert service._cache == set()

    def test_preload(self, mock_blacklist_file):
        """Test preload method initializes cache

        Args:
            mock_blacklist_file: Pytest fixture providing mock blacklist file
        """

        service = BlacklistService()
        assert service._cache is None

        with patch("src.services.blacklist.settings") as mock_settings:
            mock_settings.BLACKLIST_FILE = mock_blacklist_file

            service.preload()

            assert service._cache is not None
            assert isinstance(service._cache, set)

    def test_preload_already_loaded(self):
        """Test preload doesn't reload if already loaded

        Verifies that preload respects existing cache
        """

        service = BlacklistService()
        service._cache = {999999}

        # Preload should not change existing cache
        service.preload()

        assert service._cache == {999999}

    def test_load_valid_blacklist(self, mock_blacklist_file):
        """Test _load with valid blacklist file

        Args:
            mock_blacklist_file: Pytest fixture providing mock blacklist file
        """

        service = BlacklistService()

        with patch("src.services.blacklist.settings") as mock_settings:
            mock_settings.BLACKLIST_FILE = mock_blacklist_file

            service._load()

            assert service._cache == {111111, 222222, 333333}
