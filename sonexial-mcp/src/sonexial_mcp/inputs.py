"""Strict input models for every MCP tool.

Each model is the single source of truth for both:
  * the JSON Schema advertised to clients in list_tools(), and
  * runtime validation of incoming arguments in call_tool().

extra="forbid" rejects unknown keys so typos fail loudly instead of being ignored.
"""

from typing import Literal, Optional, List

from pydantic import BaseModel, ConfigDict, Field

LoreCategory = Literal[
    "character", "location", "faction", "item", "timeline", "magic_system", "technology"
]


class _StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PingInput(_StrictInput):
    """ping takes no arguments."""


class SearchAuthorsInput(_StrictInput):
    query: Optional[str] = Field(
        default=None, max_length=200,
        description="Text search query (searches name, bio)",
    )
    genre: Optional[str] = Field(
        default=None, max_length=100,
        description="Filter by genre (e.g., 'cyberpunk', 'space opera')",
    )
    tropes: Optional[List[str]] = Field(
        default=None, max_length=10,
        description="Filter by tropes (e.g., ['found-family', 'enemies-to-lovers'])",
    )
    verified_only: bool = Field(
        default=False, description="Only return verified authors",
    )
    limit: int = Field(
        default=10, ge=1, le=50, description="Maximum number of results",
    )


class AuthorIdInput(_StrictInput):
    author_id: str = Field(
        min_length=1, max_length=64, description="The author's canonical ID",
    )


class BookIdInput(_StrictInput):
    book_id: str = Field(
        min_length=1, max_length=64, description="The book's canonical ID",
    )


class SearchLoreInput(_StrictInput):
    query: str = Field(
        min_length=1, max_length=200, description="Search query (keyword search over title and content)",
    )
    author_id: Optional[str] = Field(default=None, max_length=64, description="Filter by author ID")
    book_id: Optional[str] = Field(default=None, max_length=64, description="Filter by book ID")
    category: Optional[LoreCategory] = Field(
        default=None, description="Filter by lore category",
    )
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")


# Tool name -> input model. The server derives list_tools() from this mapping.
TOOL_INPUTS: dict[str, type[_StrictInput]] = {
    "ping": PingInput,
    "search_authors": SearchAuthorsInput,
    "get_author": AuthorIdInput,
    "list_books": AuthorIdInput,
    "get_book": BookIdInput,
    "search_lore": SearchLoreInput,
    "get_related_authors": AuthorIdInput,
    "get_author_llms_txt": AuthorIdInput,
}
