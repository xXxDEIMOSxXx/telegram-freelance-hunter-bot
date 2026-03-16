"""Async connection to PostgreSQL using SQLAlchemy + asyncpg"""

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

engine: AsyncEngine = create_async_engine(
    settings.db_url,
    # echo=getattr(settings, "DB_ECHO", False),  # if u need database logs
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def ensure_database_exists() -> None:
    """Create database if it does not exist"""

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
            logger.info(f"Database {settings.DB_NAME} created")
        else:
            logger.info(f"Database {settings.DB_NAME} already exists")


async def create_tables() -> None:
    """Create all database tables"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created or already exist")


async def init_database() -> None:
    """Check PostgreSQL connection and init database"""

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))

        if result.scalar() == 1:
            logger.info("PostgreSQL database connection successful")
        else:
            logger.error("PostgreSQL database connection failed")
