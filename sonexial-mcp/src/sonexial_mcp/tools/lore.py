"""Lore-related tool implementations."""

from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import LoreEntry, Author, Book
from ..schemas import LoreEntrySummary, LoreEntryDetail
from ..errors import NotFoundError
from ..logging import get_logger

logger = get_logger("tools.lore")


async def search_lore(
    session: AsyncSession,
    query: str,
    author_id: Optional[str] = None,
    book_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """Search lore entries by keyword across title, content, and tags."""
    logger.info(f"search_lore: query={query}, author_id={author_id}, book_id={book_id}, category={category}")

    stmt = select(LoreEntry)

    # Text search across title, content
    search_term = f"%{query}%"
    stmt = stmt.where(
        or_(
            LoreEntry.title.ilike(search_term),
            LoreEntry.content.ilike(search_term),
        )
    )

    # Filter by author
    if author_id:
        stmt = stmt.where(LoreEntry.author_id == author_id)

    # Filter by book
    if book_id:
        stmt = stmt.where(LoreEntry.book_id == book_id)

    # Filter by category
    if category:
        stmt = stmt.where(LoreEntry.category == category)

    stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    entries = result.scalars().all()

    results = []
    for entry in entries:
        summary = LoreEntrySummary(
            id=entry.id,
            title=entry.title,
            category=entry.category,
            author_id=entry.author_id,
            book_id=entry.book_id,
            spoiler_level=entry.spoiler_level,
            tags=entry.tags or [],
        )
        results.append(summary.model_dump())

    return {
        "status": "ok",
        "results": results,
        "total": len(results),
        "limit": limit,
    }
