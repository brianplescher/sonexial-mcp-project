"""Book-related tool implementations."""

from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Book, Author
from ..schemas import BookSummary, BookDetail
from ..errors import NotFoundError
from ..logging import get_logger
from .filters import json_list_contains

logger = get_logger("tools.books")


async def list_books(session: AsyncSession, author_id: str) -> dict:
    """List all books by an author."""
    logger.info(f"list_books: author_id={author_id}")

    # Verify author exists
    author_stmt = select(Author).where(Author.id == author_id)
    author_result = await session.execute(author_stmt)
    author = author_result.scalar_one_or_none()

    if not author:
        raise NotFoundError("author", author_id)

    # Get books
    stmt = select(Book).where(Book.author_id == author_id).order_by(Book.publication_date.desc())
    result = await session.execute(stmt)
    books = result.scalars().all()

    results = []
    for book in books:
        summary = BookSummary(
            id=book.id,
            title=book.title,
            subtitle=book.subtitle,
            series_name=book.series_name,
            series_position=book.series_position,
            publication_date=book.publication_date,
            book_status=book.book_status,
            genres=book.genres or [],
            themes=book.themes or [],
            audience=book.audience or [],
            spice=book.spice,
            author_id=book.author_id,
        )
        results.append(summary.model_dump())

    return {
        "status": "ok",
        "author_id": author_id,
        "author_name": author.name,
        "results": results,
        "total": len(results),
    }


async def get_book(session: AsyncSession, book_id: str) -> dict:
    """Get full book details by ID."""
    logger.info(f"get_book: book_id={book_id}")

    stmt = select(Book).where(Book.id == book_id)
    result = await session.execute(stmt)
    book = result.scalar_one_or_none()

    if not book:
        raise NotFoundError("book", book_id)

    detail = BookDetail(
        id=book.id,
        author_id=book.author_id,
        title=book.title,
        subtitle=book.subtitle,
        series_name=book.series_name,
        series_position=book.series_position,
        publication_date=book.publication_date,
        asin=book.asin,
        isbn=book.isbn,
        blurb=book.blurb,
        genres=book.genres or [],
        tropes=book.tropes or [],
        themes=book.themes or [],
        audience=book.audience or [],
        spice=book.spice,
        cover_url=book.cover_url,
        book_status=book.book_status,
        word_count_estimate=book.word_count_estimate,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )
    return detail.model_dump()


async def search_books(
    session: AsyncSession,
    query: Optional[str] = None,
    author_id: Optional[str] = None,
    genre: Optional[str] = None,
    tropes: Optional[List[str]] = None,
    themes: Optional[List[str]] = None,
    audience: Optional[str] = None,
    spice_min: Optional[int] = None,
    spice_max: Optional[int] = None,
    limit: int = 10,
) -> dict:
    """Search books by text, author, genre, tropes, themes, audience, and spice range."""
    logger.info(
        f"search_books: query={query}, author_id={author_id}, genre={genre}, "
        f"tropes={tropes}, themes={themes}, audience={audience}, "
        f"spice={spice_min}..{spice_max}"
    )

    stmt = select(Book)

    if query:
        term = f"%{query}%"
        stmt = stmt.where(
            or_(Book.title.ilike(term), Book.subtitle.ilike(term), Book.blurb.ilike(term))
        )
    if author_id:
        stmt = stmt.where(Book.author_id == author_id)
    if genre:
        stmt = stmt.where(json_list_contains(Book.genres, genre))
    for trope in tropes or []:
        stmt = stmt.where(json_list_contains(Book.tropes, trope))
    for theme in themes or []:
        stmt = stmt.where(json_list_contains(Book.themes, theme))
    if audience:
        stmt = stmt.where(json_list_contains(Book.audience, audience))
    # NULL spice is "not rated" and is excluded whenever a spice bound is given.
    if spice_min is not None:
        stmt = stmt.where(Book.spice >= spice_min)
    if spice_max is not None:
        stmt = stmt.where(Book.spice <= spice_max)

    stmt = stmt.order_by(Book.title).limit(limit)
    result = await session.execute(stmt)
    books = result.scalars().all()

    results = [
        BookSummary(
            id=book.id,
            author_id=book.author_id,
            title=book.title,
            subtitle=book.subtitle,
            series_name=book.series_name,
            series_position=book.series_position,
            publication_date=book.publication_date,
            book_status=book.book_status,
            genres=book.genres or [],
            themes=book.themes or [],
            audience=book.audience or [],
            spice=book.spice,
        ).model_dump()
        for book in books
    ]

    return {
        "status": "ok",
        "results": results,
        "total": len(results),
        "limit": limit,
    }
