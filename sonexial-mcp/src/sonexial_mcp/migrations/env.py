"""Alembic environment.

Runs on the connection handed over by ``database.init_db`` when present, otherwise
opens its own async engine from settings (the ``alembic`` CLI path).
"""

import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from sonexial_mcp import models  # noqa: F401  (registers tables on Base.metadata)
from sonexial_mcp.config import get_settings
from sonexial_mcp.database import Base

target_metadata = Base.metadata

# render_as_batch: SQLite can't ALTER most column changes in place; batch mode
# rebuilds the table instead.
_OPTIONS = dict(target_metadata=target_metadata, render_as_batch=True, compare_type=True)


def _run(connection) -> None:
    context.configure(connection=connection, **_OPTIONS)
    with context.begin_transaction():
        context.run_migrations()


async def _run_with_own_engine() -> None:
    engine = create_async_engine(get_settings().database_url)
    try:
        async with engine.connect() as conn:
            await conn.run_sync(_run)
            await conn.commit()
    finally:
        await engine.dispose()


if context.is_offline_mode():
    context.configure(url=get_settings().database_url, literal_binds=True, **_OPTIONS)
    with context.begin_transaction():
        context.run_migrations()
else:
    connection = context.config.attributes.get("connection")
    if connection is not None:
        _run(connection)
    else:
        asyncio.run(_run_with_own_engine())
