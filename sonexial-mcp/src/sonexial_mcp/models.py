"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .database import Base


def generate_id() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def now() -> datetime:
    """Current UTC datetime."""
    return datetime.utcnow()


class Author(Base):
    """Indie author entity."""
    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_id)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    pen_names: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    website: Mapped[Optional[str]] = mapped_column(String(512))
    bio_short: Mapped[Optional[str]] = mapped_column(Text)
    bio_long: Mapped[Optional[str]] = mapped_column(Text)
    genres: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    tropes: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    themes: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    audience: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    verification_status: Mapped[str] = mapped_column(
        String(32), default="unverified", index=True
    )
    source_urls: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    # Relationships
    books: Mapped[List["Book"]] = relationship("Book", back_populates="author", lazy="selectin")
    lore_entries: Mapped[List["LoreEntry"]] = relationship("LoreEntry", back_populates="author", lazy="selectin")

    __table_args__ = (
        Index("idx_author_genres", "genres", postgresql_using="gin"),
    )


class Book(Base):
    """Book entity."""
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_id)
    author_id: Mapped[str] = mapped_column(String(64), ForeignKey("authors.id"), index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    subtitle: Mapped[Optional[str]] = mapped_column(String(512))
    series_name: Mapped[Optional[str]] = mapped_column(String(256))
    series_position: Mapped[Optional[int]] = mapped_column(Integer)
    publication_date: Mapped[Optional[str]] = mapped_column(String(32))
    asin: Mapped[Optional[str]] = mapped_column(String(32))
    isbn: Mapped[Optional[str]] = mapped_column(String(32))
    blurb: Mapped[Optional[str]] = mapped_column(Text)
    genres: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    tropes: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    cover_url: Mapped[Optional[str]] = mapped_column(String(512))
    book_status: Mapped[str] = mapped_column(String(32), default="published")
    word_count_estimate: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    # Relationships
    author: Mapped["Author"] = relationship("Author", back_populates="books")
    lore_entries: Mapped[List["LoreEntry"]] = relationship("LoreEntry", back_populates="book", lazy="selectin")


class LoreEntry(Base):
    """Lore entry for a book or author's universe."""
    __tablename__ = "lore_entries"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_id)
    author_id: Mapped[str] = mapped_column(String(64), ForeignKey("authors.id"), index=True)
    book_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("books.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(256), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    canonical: Mapped[bool] = mapped_column(Boolean, default=True)
    spoiler_level: Mapped[str] = mapped_column(String(16), default="none")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    # Relationships
    author: Mapped["Author"] = relationship("Author", back_populates="lore_entries")
    book: Mapped[Optional["Book"]] = relationship("Book", back_populates="lore_entries")


class AuthorRelationship(Base):
    """Relationship between two authors."""
    __tablename__ = "author_relationships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_id)
    source_author_id: Mapped[str] = mapped_column(String(64), ForeignKey("authors.id"), index=True)
    target_author_id: Mapped[str] = mapped_column(String(64), ForeignKey("authors.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(64), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    __table_args__ = (
        Index("idx_relationship_pair", "source_author_id", "target_author_id"),
    )
