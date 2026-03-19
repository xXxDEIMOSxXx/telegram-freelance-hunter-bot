"""Async connection to PostgreSQL using SQLAlchemy + asyncpg

This module handles:
- Async engine creation with connection pooling
- Database and table initialization
- Session management for async database operations
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings
from src.database.models import Base
from src.utils.logger import logger

# Async engine for PostgreSQL with pooling configuration
engine: AsyncEngine = create_async_engine(
    settings.db_url,
    # echo=getattr(settings, "DB_ECHO", False),  # if u need database logs
    future=True,
    pool_size=5,
    pool_timeout=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# Async session factory for creating database sessions
async_session: async_sessionmaker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def ensure_database_exists() -> None:
    """
    Create PostgreSQL database if it doesn't exist

    Connects to the PostgreSQL service database to check if the application
    database exists. If not, creates it. Uses synchronous connection since
    database creation requires AUTOCOMMIT isolation level

    Raises:
        Exception: If database connection or creation fails

    Side effects:
        - Creates the database specified in settings.DB_NAME
        - Logs success/info messages via logger
    """

    sync_url = settings.db_url.replace(f"/{settings.DB_NAME}", "/postgres").replace(
        "postgresql+asyncpg://", "postgresql://"
    )

    sync_engine = create_engine(sync_url, isolation_level="AUTOCOMMIT")

    with sync_engine.connect() as conn:
        # We need connect to service postgresql database, and use simple select
        # to check if our database is existed (PostgreSQL don't have if exist func)
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:db_name"),
            {"db_name": settings.DB_NAME},
        )

        exists = result.scalar() is not None

        if not exists:
            conn.execute(text(f'CREATE DATABASE "{settings.DB_NAME}"'))
            logger.success(f"Database {settings.DB_NAME} created")
        else:
            logger.success(f"Database {settings.DB_NAME} already exists")


async def create_tables() -> None:
    """
    Create all database tables defined in SQLAlchemy models

    Uses the declarative Base metadata to create tables based on
    registered models (TelegramMessage). Creates tables only if they
    don't exist

    Raises:
        Exception: If table creation fails

    Side effects:
        - Creates tables in the database
        - Logs success message via logger
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.success("Database tables created or already exist")


async def init_database() -> None:
    """
    Initialize PostgreSQL database connection and setup

    Performs full database initialization:
    1. Ensures database exists (creates if needed)
    2. Creates all required tables
    3. Tests the connection with a simple SELECT query

    This function should be called during application bootstrap

    Raises:
        Exception: If any initialization step fails (logged but not re-raised)

    Side effects:
        - May create database and tables
        - Logs connection status via logger
    """

    try:
        ensure_database_exists()
        await create_tables()

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))

        if result.scalar() == 1:
            logger.success("PostgreSQL database connection successful")
        else:
            logger.error("PostgreSQL database connection failed")
    except Exception as e:
        logger.error("PostgreSQL database connection failed: %s", e)
