"""Strict input models for every MCP tool.

Each model is the single source of truth for both:
  * the JSON Schema advertised to clients in list_tools(), and
  * runtime validation of incoming arguments in call_tool().

extra="forbid" rejects unknown keys so typos fail loudly instead of being ignored.
"""

from typing import Literal, Optional, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

LoreCategory = Literal[
    "character", "location", "faction", "item", "timeline", "magic_system", "technology"
]

Audience = Literal["all-ages", "young-adult", "new-adult", "adult"]

SPICE_RUBRIC = (
    "Romantic/sexual content heat, 0-5. 0 = none or fade-to-black; "
    "1 = romance present, no on-page sex; 2 = brief, non-explicit on-page intimacy; "
    "3 = on-page scenes, moderate detail; 4 = frequent explicit scenes; "
    "5 = very explicit throughout."
)


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
    themes: Optional[List[str]] = Field(
        default=None, max_length=10,
        description="Filter by author-level themes (e.g., ['memory', 'climate'])",
    )
    audience: Optional[Audience] = Field(
        default=None, description="Filter by author-level audience",
    )
    verified_only: bool = Field(
        default=False, description="Only return verified authors",
    )
    limit: int = Field(
        default=10, ge=1, le=50, description="Maximum number of results",
    )


class SearchBooksInput(_StrictInput):
    query: Optional[str] = Field(
        default=None, max_length=200,
        description="Text search over title, subtitle, and blurb",
    )
    author_id: Optional[str] = Field(
        default=None, max_length=64, description="Limit to one author's books",
    )
    genre: Optional[str] = Field(default=None, max_length=100, description="Filter by genre")
    tropes: Optional[List[str]] = Field(
        default=None, max_length=10, description="Filter by tropes (all must match)",
    )
    themes: Optional[List[str]] = Field(
        default=None, max_length=10, description="Filter by themes (all must match)",
    )
    audience: Optional[Audience] = Field(default=None, description="Filter by audience")
    spice_min: Optional[int] = Field(
        default=None, ge=0, le=5, description=SPICE_RUBRIC,
    )
    spice_max: Optional[int] = Field(
        default=None, ge=0, le=5, description="Upper bound of the spice range (inclusive)",
    )
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")

    @model_validator(mode="after")
    def _check_spice_range(self):
        if self.spice_min is not None and self.spice_max is not None and self.spice_min > self.spice_max:
            raise ValueError("spice_min must be less than or equal to spice_max")
        return self


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
    "search_books": SearchBooksInput,
    "get_author": AuthorIdInput,
    "list_books": AuthorIdInput,
    "get_book": BookIdInput,
    "search_lore": SearchLoreInput,
    "get_related_authors": AuthorIdInput,
    "get_author_llms_txt": AuthorIdInput,
}
