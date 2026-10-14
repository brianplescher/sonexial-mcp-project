"""The JSON-contains helper must match whole elements and treat LIKE wildcards literally."""

from sqlalchemy import Column, Integer, JSON, String, select
from sqlalchemy.orm import declarative_base

from sonexial_mcp.tools.filters import json_list_contains

Base = declarative_base()


class Thing(Base):
    __tablename__ = "things"
    id = Column(Integer, primary_key=True)
    tags = Column(JSON)


def _sql(value):
    return str(select(Thing).where(json_list_contains(Thing.tags, value)).compile(compile_kwargs={"literal_binds": True}))


def test_wildcards_are_escaped():
    sql = _sql("50%_off")
    assert "50\\%\\_off" in sql
    assert "ESCAPE" in sql.upper()


def test_pattern_is_quoted_element_match():
    sql = _sql("memory")
    assert '"memory"' in sql
