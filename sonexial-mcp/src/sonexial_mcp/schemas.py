"""Pydantic schemas for data validation and serialization."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# Author Schemas

class AuthorSummary(BaseModel):
    """Brief author information for search results."""
    id: str
    name: str
    slug: str
    genres: List[str] = Field(default_factory=list)
    tropes: List[str] = Field(default_factory=list)
    verification_status: str
    website: Optional[str] = None
    match_reason: Optional[str] = None


class AuthorProfile(BaseModel):
    """Full author profile."""
    id: str
    slug: str
    name: str
    pen_names: List[str] = Field(default_factory=list)
    website: Optional[str] = None
    bio_short: Optional[str] = None
    bio_long: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    tropes: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    audience: List[str] = Field(default_factory=list)
    verification_status: str
    source_urls: List[str] = Field(default_factory=list)
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Book Schemas

class BookSummary(BaseModel):
    """Brief book information."""
    id: str
    title: str
    subtitle: Optional[str] = None
    series_name: Optional[str] = None
    series_position: Optional[int] = None
    publication_date: Optional[str] = None
    book_status: str
    genres: List[str] = Field(default_factory=list)


class BookDetail(BaseModel):
    """Full book details."""
    id: str
    author_id: str
    title: str
    subtitle: Optional[str] = None
    series_name: Optional[str] = None
    series_position: Optional[int] = None
    publication_date: Optional[str] = None
    asin: Optional[str] = None
    isbn: Optional[str] = None
    blurb: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    tropes: List[str] = Field(default_factory=list)
    cover_url: Optional[str] = None
    book_status: str
    word_count_estimate: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# Lore Schemas

class LoreEntrySummary(BaseModel):
    """Brief lore entry information."""
    id: str
    title: str
    category: str
    author_id: str
    book_id: Optional[str] = None
    spoiler_level: str
    tags: List[str] = Field(default_factory=list)


class LoreEntryDetail(BaseModel):
    """Full lore entry details."""
    id: str
    author_id: str
    book_id: Optional[str] = None
    title: str
    category: str
    content: str
    tags: List[str] = Field(default_factory=list)
    canonical: bool
    spoiler_level: str
    created_at: datetime
    updated_at: datetime


# Relationship Schemas

class AuthorRelationshipSchema(BaseModel):
    """Author relationship information."""
    source_author_id: str
    target_author_id: str
    relationship_type: str
    weight: float
    notes: Optional[str] = None
    target_author_name: Optional[str] = None
    target_author_genres: List[str] = Field(default_factory=list)


# Response Schemas

class SearchResponse(BaseModel):
    """Generic search response."""
    status: str = "ok"
    results: List[Any]
    total: int
    limit: int


class PingResponse(BaseModel):
    """Ping/health check response."""
    status: str = "ok"
    service: str = "sonexial-author-mcp"
    version: str = "0.1.0"
