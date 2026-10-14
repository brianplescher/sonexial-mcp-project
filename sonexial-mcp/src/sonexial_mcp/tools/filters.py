"""Shared query helpers for JSON list columns.

Matches a quoted element inside a JSON array stored as text. LIKE wildcards in the
search value are escaped so "%" or "_" in user input match literally.
"""

from sqlalchemy import ColumnElement, Text, cast


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def json_list_contains(column, value: str) -> ColumnElement:
    """Rows whose JSON array column contains the given string element."""
    # Cast to text first: LIKE is not defined on the JSON type itself (SQLAlchemy warns,
    # and Postgres json/jsonb rejects it), but the text form of the array contains the quoted token.
    return cast(column, Text).like(f'%"{_escape_like(value)}"%', escape="\\")
