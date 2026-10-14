"""Author-related tool implementations."""

from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Author, AuthorRelationship
from ..schemas import AuthorSummary, AuthorProfile, AuthorRelationshipSchema
from ..errors import NotFoundError
from ..logging import get_logger
from .filters import json_list_contains

logger = get_logger("tools.authors")


async def search_authors(
    session: AsyncSession,
    query: Optional[str] = None,
    genre: Optional[str] = None,
    tropes: Optional[List[str]] = None,
    themes: Optional[List[str]] = None,
    audience: Optional[str] = None,
    verified_only: bool = False,
    limit: int = 10,
) -> dict:
    """Search for authors by query, genre, tropes, themes, audience, and verification status."""
    logger.info(
        f"search_authors: query={query}, genre={genre}, tropes={tropes}, "
        f"themes={themes}, audience={audience}, verified_only={verified_only}"
    )

    stmt = select(Author)

    # Text search across name, bio, genres, tropes
    if query:
        search_term = f"%{query}%"
        stmt = stmt.where(
            or_(
                Author.name.ilike(search_term),
                Author.bio_short.ilike(search_term),
                Author.bio_long.ilike(search_term),
            )
        )

    if genre:
        stmt = stmt.where(json_list_contains(Author.genres, genre))
    for trope in tropes or []:
        stmt = stmt.where(json_list_contains(Author.tropes, trope))
    for theme in themes or []:
        stmt = stmt.where(json_list_contains(Author.themes, theme))
    if audience:
        stmt = stmt.where(json_list_contains(Author.audience, audience))

    # Filter by verification status
    if verified_only:
        stmt = stmt.where(
            Author.verification_status.in_(["verified_human", "sonexial_verified"])
        )

    stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    authors = result.scalars().all()

    results = []
    for author in authors:
        match_reason = _build_match_reason(author, query, genre, tropes)
        summary = AuthorSummary(
            id=author.id,
            name=author.name,
            slug=author.slug,
            genres=author.genres or [],
            tropes=author.tropes or [],
            verification_status=author.verification_status,
            website=author.website,
            match_reason=match_reason,
        )
        results.append(summary.model_dump())

    return {
        "status": "ok",
        "results": results,
        "total": len(results),
        "limit": limit,
    }


async def get_author(session: AsyncSession, author_id: str) -> dict:
    """Get full author profile by ID."""
    logger.info(f"get_author: author_id={author_id}")

    stmt = select(Author).where(Author.id == author_id)
    result = await session.execute(stmt)
    author = result.scalar_one_or_none()

    if not author:
        raise NotFoundError("author", author_id)

    profile = AuthorProfile(
        id=author.id,
        slug=author.slug,
        name=author.name,
        pen_names=author.pen_names or [],
        website=author.website,
        bio_short=author.bio_short,
        bio_long=author.bio_long,
        genres=author.genres or [],
        tropes=author.tropes or [],
        themes=author.themes or [],
        audience=author.audience or [],
        verification_status=author.verification_status,
        source_urls=author.source_urls or [],
        last_verified_at=author.last_verified_at,
        created_at=author.created_at,
        updated_at=author.updated_at,
    )
    return profile.model_dump()


async def get_related_authors(session: AsyncSession, author_id: str) -> dict:
    """Find authors related to a given author."""
    logger.info(f"get_related_authors: author_id={author_id}")

    # First check if author exists
    stmt = select(Author).where(Author.id == author_id)
    result = await session.execute(stmt)
    source_author = result.scalar_one_or_none()

    if not source_author:
        raise NotFoundError("author", author_id)

    # Check explicit relationships
    stmt = select(AuthorRelationship).where(
        AuthorRelationship.source_author_id == author_id
    ).order_by(AuthorRelationship.weight.desc())
    result = await session.execute(stmt)
    relationships = result.scalars().all()

    results = []

    if relationships:
        for rel in relationships:
            target_stmt = select(Author).where(Author.id == rel.target_author_id)
            target_result = await session.execute(target_stmt)
            target = target_result.scalar_one_or_none()
            if target:
                results.append(AuthorRelationshipSchema(
                    source_author_id=rel.source_author_id,
                    target_author_id=rel.target_author_id,
                    relationship_type=rel.relationship_type,
                    weight=rel.weight,
                    notes=rel.notes,
                    target_author_name=target.name,
                    target_author_genres=target.genres or [],
                ).model_dump())

    # If no explicit relationships, find by genre/trope similarity
    if not results:
        stmt = select(Author).where(Author.id != author_id)
        all_result = await session.execute(stmt)
        all_authors = all_result.scalars().all()

        source_genres = set(source_author.genres or [])
        source_tropes = set(source_author.tropes or [])

        scored = []
        for author in all_authors:
            author_genres = set(author.genres or [])
            author_tropes = set(author.tropes or [])
            genre_overlap = len(source_genres & author_genres)
            trope_overlap = len(source_tropes & author_tropes)
            score = genre_overlap * 2 + trope_overlap
            if score > 0:
                scored.append((author, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        for author, score in scored[:10]:
            results.append(AuthorRelationshipSchema(
                source_author_id=author_id,
                target_author_id=author.id,
                relationship_type="similar_to",
                weight=float(score),
                notes=f"Similarity score: {score} (genre overlap: {len(source_genres & set(author.genres or []))}, trope overlap: {len(source_tropes & set(author.tropes or []))})",
                target_author_name=author.name,
                target_author_genres=author.genres or [],
            ).model_dump())

    return {
        "status": "ok",
        "results": results,
        "total": len(results),
    }


async def get_author_llms_txt(session: AsyncSession, author_id: str) -> dict:
    """Generate a clean Markdown summary of an author for AI consumption."""
    logger.info(f"get_author_llms_txt: author_id={author_id}")

    stmt = select(Author).where(Author.id == author_id)
    result = await session.execute(stmt)
    author = result.scalar_one_or_none()

    if not author:
        raise NotFoundError("author", author_id)

    # Build markdown
    lines = [
        f"# {author.name}",
        "",
    ]

    if author.pen_names:
        lines.append(f"**Pen names:** {', '.join(author.pen_names)}")
        lines.append("")

    if author.website:
        lines.append(f"**Website:** {author.website}")
        lines.append("")

    lines.append(f"**Verification:** {author.verification_status}")
    lines.append("")

    if author.genres:
        lines.append(f"**Genres:** {', '.join(author.genres)}")
        lines.append("")

    if author.tropes:
        lines.append(f"**Tropes:** {', '.join(author.tropes)}")
        lines.append("")

    if author.themes:
        lines.append(f"**Themes:** {', '.join(author.themes)}")
        lines.append("")

    if author.bio_short:
        lines.append("## About")
        lines.append("")
        lines.append(author.bio_short)
        lines.append("")

    if author.books:
        lines.append("## Books")
        lines.append("")
        for book in author.books:
            title = book.title
            if book.subtitle:
                title += f": {book.subtitle}"
            series_info = ""
            if book.series_name:
                series_info = f" (Series: {book.series_name}"
                if book.series_position:
                    series_info += f", #{book.series_position}"
                series_info += ")"
            lines.append(f"- **{title}**{series_info} [{book.book_status}]")
            if book.blurb:
                lines.append(f"  {book.blurb[:200]}...")
        lines.append("")

    content = "\n".join(lines)

    return {
        "status": "ok",
        "content": content,
        "format": "markdown",
        "author_id": author_id,
        "author_name": author.name,
    }


def _build_match_reason(author: Author, query: Optional[str], genre: Optional[str], tropes: Optional[List[str]]) -> str:
    """Build a human-readable match reason."""
    reasons = []
    if query and query.lower() in (author.name or "").lower():
        reasons.append("name match")
    if query and author.bio_short and query.lower() in author.bio_short.lower():
        reasons.append("bio match")
    if genre and genre in (author.genres or []):
        reasons.append(f"genre: {genre}")
    if tropes:
        matching = [t for t in tropes if t in (author.tropes or [])]
        if matching:
            reasons.append(f"tropes: {', '.join(matching)}")
    return "; ".join(reasons) if reasons else "general match"
