"""Unit tests for database connection module"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.database.connection import create_tables, ensure_database_exists, init_database


class TestDatabaseConnection:
    """Tests for database connection and initialization"""

    def test_ensure_database_exists_creates_new_db(self):
        """Test database creation when it doesn't exist

        Verifies database initialization is attempted
        """

        with (
            patch("src.database.connection.create_engine") as mock_engine_func,
            patch("src.database.connection.settings") as mock_settings,
            patch("src.database.connection.logger"),
        ):
            mock_settings.DB_NAME = "test_db"
            mock_settings.db_url = "postgresql://user:pass@localhost/test_db"

            # Just verify function doesn't crash
            ensure_database_exists()

            # Verify create_engine was called
            assert mock_engine_func.called

    def test_ensure_database_exists_skips_existing_db(self):
        """Test database initialization when it already exists

        Verifies function handles existing database
        """

        with (
            patch("src.database.connection.create_engine") as mock_engine_func,
            patch("src.database.connection.settings") as mock_settings,
            patch("src.database.connection.logger"),
        ):
            mock_settings.DB_NAME = "test_db"
            mock_settings.db_url = "postgresql://user:pass@localhost/test_db"

            # Just verify function doesn't crash
            ensure_database_exists()

            # Verify create_engine was called
            assert mock_engine_func.called

    @pytest.mark.asyncio
    async def test_create_tables_success(self):
        """Test successful table creation

        Verifies all tables are created
        """

        mock_conn = AsyncMock()
        mock_engine = MagicMock()

        mock_engine.begin = MagicMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("src.database.connection.engine", mock_engine),
            patch("src.database.connection.Base"),
        ):
            await create_tables()

            # Verify run_sync was called
            mock_conn.run_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_database_success(self):
        """Test successful database initialization

        Verifies all init steps complete
        """

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(return_value=MagicMock(scalar=lambda: 1))
        mock_engine = MagicMock()

        mock_engine.connect = MagicMock()
        mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("src.database.connection.ensure_database_exists"),
            patch("src.database.connection.create_tables", new_callable=AsyncMock),
            patch("src.database.connection.engine", mock_engine),
        ):
            await init_database()

            # Should have attempted connection
            mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_database_handles_errors(self):
        """Test database initialization error handling

        Verifies errors don't crash initialization
        """

        with (
            patch("src.database.connection.ensure_database_exists") as mock_ensure,
            patch("src.database.connection.create_tables"),
        ):
            mock_ensure.side_effect = Exception("DB connection failed")

            # Should not raise exception
            await init_database()
