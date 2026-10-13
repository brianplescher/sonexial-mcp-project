"""MCP Server implementation using the official MCP SDK."""

import json
from typing import Any, Optional, List
from mcp.server import Server
from mcp.types import Tool, TextContent

from .config import get_settings
from .database import get_session_factory, init_db
from .logging import get_logger
from .tools.health import ping
from .tools.authors import search_authors, get_author, get_related_authors, get_author_llms_txt
from .tools.books import list_books, get_book
from .tools.lore import search_lore
from .errors import SonexialError

logger = get_logger("server")


def create_server() -> Server:
    """Create and configure the MCP server."""
    settings = get_settings()

    server = Server("sonexial-author-mcp")

    # Register tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="ping",
                description="Health check. Returns service status and version.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="search_authors",
                description="Search for indie authors by query, genre, tropes, and verification status.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text search query (searches name, bio)",
                        },
                        "genre": {
                            "type": "string",
                            "description": "Filter by genre (e.g., 'cyberpunk', 'space opera')",
                        },
                        "tropes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tropes (e.g., ['found-family', 'enemies-to-lovers'])",
                        },
                        "verified_only": {
                            "type": "boolean",
                            "description": "Only return verified authors",
                            "default": False,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                },
            ),
            Tool(
                name="get_author",
                description="Get full author profile by ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "The author's canonical ID",
                        },
                    },
                    "required": ["author_id"],
                },
            ),
            Tool(
                name="list_books",
                description="List all books by an author.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "The author's canonical ID",
                        },
                    },
                    "required": ["author_id"],
                },
            ),
            Tool(
                name="get_book",
                description="Get full book details by ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "book_id": {
                            "type": "string",
                            "description": "The book's canonical ID",
                        },
                    },
                    "required": ["book_id"],
                },
            ),
            Tool(
                name="search_lore",
                description="Search lore entries by keyword across title, content, and tags.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (keyword search)",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by author ID",
                        },
                        "book_id": {
                            "type": "string",
                            "description": "Filter by book ID",
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category (character, location, faction, item, timeline, magic_system, technology)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_related_authors",
                description="Find authors related to a given author based on explicit relationships or genre/trope similarity.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "The author's canonical ID",
                        },
                    },
                    "required": ["author_id"],
                },
            ),
            Tool(
                name="get_author_llms_txt",
                description="Get a clean Markdown summary of an author suitable for AI consumption. Functions like a dynamic llms.txt for the author.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "author_id": {
                            "type": "string",
                            "description": "The author's canonical ID",
                        },
                    },
                    "required": ["author_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        logger.info(f"Tool call: {name} with args: {json.dumps(arguments, default=str)[:200]}")

        try:
            result = await _execute_tool(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
        except SonexialError as e:
            logger.warning(f"Tool error: {name} - {e.code}: {e.message}")
            return [TextContent(type="text", text=json.dumps(e.to_response().model_dump(), indent=2))]
        except Exception as e:
            logger.error(f"Unexpected error in tool {name}: {str(e)}")
            error_response = {
                "status": "error",
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                },
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def _execute_tool(name: str, arguments: dict) -> dict:
        """Execute a tool by name with the given arguments."""
        session_factory = get_session_factory()

        if name == "ping":
            return ping()

        async with session_factory() as session:
            if name == "search_authors":
                return await search_authors(
                    session,
                    query=arguments.get("query"),
                    genre=arguments.get("genre"),
                    tropes=arguments.get("tropes"),
                    verified_only=arguments.get("verified_only", False),
                    limit=arguments.get("limit", 10),
                )
            elif name == "get_author":
                return await get_author(session, arguments["author_id"])
            elif name == "list_books":
                return await list_books(session, arguments["author_id"])
            elif name == "get_book":
                return await get_book(session, arguments["book_id"])
            elif name == "search_lore":
                return await search_lore(
                    session,
                    query=arguments["query"],
                    author_id=arguments.get("author_id"),
                    book_id=arguments.get("book_id"),
                    category=arguments.get("category"),
                    limit=arguments.get("limit", 10),
                )
            elif name == "get_related_authors":
                return await get_related_authors(session, arguments["author_id"])
            elif name == "get_author_llms_txt":
                return await get_author_llms_txt(session, arguments["author_id"])
            else:
                return {
                    "status": "error",
                    "error": {
                        "code": "unknown_tool",
                        "message": f"Unknown tool: {name}",
                    },
                }

    return server
