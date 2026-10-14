"""Migrations must build exactly the schema the models describe."""

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from sonexial_mcp import models  # noqa: F401
from sonexial_mcp.database import Base, _upgrade_to_head, alembic_config


@pytest.fixture
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path / 'migrate.db'}")
    yield eng
    eng.dispose()


def _head() -> str:
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def _revision(conn) -> str:
    return MigrationContext.configure(conn).get_current_revision()


def test_upgrade_matches_models(engine):
    with engine.begin() as conn:
        _upgrade_to_head(conn)
    with engine.connect() as conn:
        assert compare_metadata(MigrationContext.configure(conn), Base.metadata) == []
        assert _revision(conn) == _head()


def test_upgrade_is_idempotent(engine):
    for _ in range(2):
        with engine.begin() as conn:
            _upgrade_to_head(conn)


def test_downgrade_to_base_removes_tables(engine):
    with engine.begin() as conn:
        _upgrade_to_head(conn)
        command.downgrade(alembic_config(conn), "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}


def test_pre_migration_database_matching_schema_is_adopted(engine):
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    with engine.begin() as conn:
        _upgrade_to_head(conn)
    with engine.connect() as conn:
        assert _revision(conn) == _head()


def test_pre_migration_database_with_old_schema_is_refused(engine):
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
        conn.execute(text("ALTER TABLE books DROP COLUMN themes"))
    with engine.begin() as conn, pytest.raises(RuntimeError, match="predates migrations"):
        _upgrade_to_head(conn)
