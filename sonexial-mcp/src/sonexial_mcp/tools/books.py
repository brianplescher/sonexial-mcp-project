"""Book-related tool implementations."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Book, Author
from ..schemas import BookSummary, BookDetail
from ..errors import NotFoundError
from ..logging import get_logger

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
        cover_url=book.cover_url,
        book_status=book.book_status,
        word_count_estimate=book.word_count_estimate,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )
    return detail.model_dump()
