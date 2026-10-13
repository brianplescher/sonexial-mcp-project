"""MCP server implementation using the official MCP Python SDK (mcp 1.x)."""

import json
from typing import Any

from pydantic import ValidationError
from mcp.server import Server
from mcp.types import Tool, TextContent

from .config import get_settings
from .database import get_session_factory
from .inputs import TOOL_INPUTS
from .logging import get_logger
from .tools.health import ping
from .tools.authors import search_authors, get_author, get_related_authors, get_author_llms_txt
from .tools.books import list_books, get_book
from .tools.lore import search_lore
from .errors import SonexialError, InvalidInputError

logger = get_logger("server")

TOOL_DESCRIPTIONS: dict[str, str] = {
    "ping": "Health check. Returns service status and version.",
    "search_authors": "Search for indie authors by query, genre, tropes, and verification status.",
    "get_author": "Get full author profile by ID.",
    "list_books": "List all books by an author.",
    "get_book": "Get full book details by ID.",
    "search_lore": (
        "Search lore entries by keyword across title and content, "
        "with optional author, book, and category filters."
    ),
    "get_related_authors": (
        "Find authors related to a given author based on explicit relationships "
        "or genre/trope similarity."
    ),
    "get_author_llms_txt": (
        "Get a clean Markdown summary of an author suitable for AI consumption. "
        "Functions like a dynamic llms.txt for the author."
    ),
}


def _build_tool_list() -> list[Tool]:
    """Derive the advertised tool list from the strict input models."""
    return [
        Tool(
            name=name,
            description=TOOL_DESCRIPTIONS[name],
            inputSchema=model.model_json_schema(),
        )
        for name, model in TOOL_INPUTS.items()
    ]


def _error_content(code: str, message: str, field: str | None = None) -> list[TextContent]:
    payload = {"status": "error", "error": {"code": code, "message": message}}
    if field:
        payload["error"]["details"] = {"field": field}
    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


def create_server() -> Server:
    """Create and configure the MCP server."""
    get_settings()  # fail fast on bad configuration

    server = Server("sonexial-author-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools with strict JSON Schemas."""
        return _build_tool_list()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        """Validate arguments against the tool's model, then execute."""
        logger.info(f"Tool call: {name}")

        model = TOOL_INPUTS.get(name)
        if model is None:
            return _error_content("unknown_tool", f"Unknown tool: {name}")

        # Validate before touching the database. Unknown or mistyped fields are rejected.
        try:
            validated = model.model_validate(arguments or {})
        except ValidationError as e:
            first = e.errors()[0]
            field = ".".join(str(p) for p in first["loc"]) or None
            err = InvalidInputError(f"{first['msg']} (field: {field})" if field else first["msg"], field=field)
            logger.warning(f"Invalid input for {name}: {err.message}")
            return [TextContent(type="text", text=json.dumps(err.to_response().model_dump(), indent=2))]

        try:
            result = await _execute_tool(name, validated.model_dump())
            return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
        except SonexialError as e:
            logger.warning(f"Tool error: {name} - {e.code}: {e.message}")
            return [TextContent(type="text", text=json.dumps(e.to_response().model_dump(), indent=2))]
        except Exception:
            logger.exception(f"Unexpected error in tool {name}")
            return _error_content("internal_error", "An unexpected error occurred.")

    async def _execute_tool(name: str, args: dict[str, Any]) -> dict:
        """Dispatch a validated tool call."""
        if name == "ping":
            return ping()

        session_factory = get_session_factory()
        async with session_factory() as session:
            if name == "search_authors":
                return await search_authors(
                    session,
                    query=args["query"],
                    genre=args["genre"],
                    tropes=args["tropes"],
                    verified_only=args["verified_only"],
                    limit=args["limit"],
                )
            if name == "get_author":
                return await get_author(session, args["author_id"])
            if name == "list_books":
                return await list_books(session, args["author_id"])
            if name == "get_book":
                return await get_book(session, args["book_id"])
            if name == "search_lore":
                return await search_lore(
                    session,
                    query=args["query"],
                    author_id=args["author_id"],
                    book_id=args["book_id"],
                    category=args["category"],
                    limit=args["limit"],
                )
            if name == "get_related_authors":
                return await get_related_authors(session, args["author_id"])
            if name == "get_author_llms_txt":
                return await get_author_llms_txt(session, args["author_id"])
        raise SonexialError("unknown_tool", f"Unknown tool: {name}")

    return server
