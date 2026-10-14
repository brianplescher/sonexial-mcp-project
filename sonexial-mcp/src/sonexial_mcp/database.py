"""Database connection and session management."""

from pathlib import Path
from typing import AsyncGenerator

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings
from .logging import get_logger

logger = get_logger("database")


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Global engine and session factory
_engine = None
_session_factory = None


def get_engine():
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        _engine = create_async_engine(
            settings.database_url,
            # echo=True makes SQLAlchemy write SQL to stdout, which corrupts the
            # stdio protocol stream. SQL logging is opt-in via the logger instead.
            echo=False,
            connect_args=connect_args,
        )
        logger.info(f"Database engine created: {settings.database_url.split('://')[0]}://...")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session (for dependency injection)."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


MIGRATIONS_DIR = Path(__file__).parent / "migrations"
BASELINE_REVISION = "0001_baseline"


def alembic_config(connection=None) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    cfg.attributes["connection"] = connection
    return cfg


def _upgrade_to_head(connection) -> None:
    from . import models  # noqa: F401  (registers tables on Base.metadata)

    cfg = alembic_config(connection)
    tables = set(inspect(connection).get_table_names())
    if "authors" in tables and "alembic_version" not in tables:
        # Database created by the old create_all() path, before migrations existed.
        # Adopt it only if it already matches the baseline schema exactly.
        diffs = compare_metadata(MigrationContext.configure(connection), Base.metadata)
        if diffs:
            raise RuntimeError(
                "Database predates migrations and does not match the current schema "
                f"({len(diffs)} differences). Delete it and re-seed, or migrate it by hand."
            )
        command.stamp(cfg, BASELINE_REVISION)
        logger.info("Adopted pre-migration database at baseline revision.")
    command.upgrade(cfg, "head")


async def init_db():
    """Bring the database schema up to the latest migration."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(_upgrade_to_head)
    logger.info("Database schema is up to date.")


async def close_db():
    """Close database connections."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed.")
