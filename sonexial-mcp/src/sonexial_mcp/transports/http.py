"""HTTP transport for remote MCP clients."""

import json
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from ..config import get_settings
from ..database import init_db
from ..auth import verify_api_key, is_auth_enabled
from ..errors import AuthenticationError, SonexialError
from ..logging import get_logger

logger = get_logger("transports.http")


def create_http_app() -> Starlette:
    """Create the HTTP application with MCP endpoint."""
    settings = get_settings()

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]

    async def healthz(request: Request) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({"status": "ok", "service": "sonexial-author-mcp", "version": "0.1.0"})

    async def mcp_endpoint(request: Request) -> JSONResponse:
        """MCP endpoint for tool calls over HTTP."""
        # Authentication
        if is_auth_enabled():
            try:
                auth_header = request.headers.get("authorization")
                verify_api_key(auth_header)
            except AuthenticationError as e:
                return JSONResponse(
                    e.to_response().model_dump(),
                    status_code=401,
                )

        try:
            body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(
                {"status": "error", "error": {"code": "invalid_json", "message": "Request body must be valid JSON."}},
                status_code=400,
            )

        tool_name = body.get("tool")
        arguments = body.get("arguments", {})

        if not tool_name:
            return JSONResponse(
                {"status": "error", "error": {"code": "missing_tool", "message": "Missing 'tool' field in request body."}},
                status_code=400,
            )

        # Import here to avoid circular imports
        from ..server import create_server

        try:
            # Execute tool directly
            from ..tools.health import ping
            from ..tools.authors import search_authors, get_author, get_related_authors, get_author_llms_txt
            from ..tools.books import list_books, get_book
            from ..tools.lore import search_lore
            from ..database import get_session_factory

            if tool_name == "ping":
                result = ping()
                return JSONResponse(result)

            session_factory = get_session_factory()
            async with session_factory() as session:
                if tool_name == "search_authors":
                    result = await search_authors(
                        session,
                        query=arguments.get("query"),
                        genre=arguments.get("genre"),
                        tropes=arguments.get("tropes"),
                        verified_only=arguments.get("verified_only", False),
                        limit=arguments.get("limit", 10),
                    )
                elif tool_name == "get_author":
                    result = await get_author(session, arguments.get("author_id", ""))
                elif tool_name == "list_books":
                    result = await list_books(session, arguments.get("author_id", ""))
                elif tool_name == "get_book":
                    result = await get_book(session, arguments.get("book_id", ""))
                elif tool_name == "search_lore":
                    result = await search_lore(
                        session,
                        query=arguments.get("query", ""),
                        author_id=arguments.get("author_id"),
                        book_id=arguments.get("book_id"),
                        category=arguments.get("category"),
                        limit=arguments.get("limit", 10),
                    )
                elif tool_name == "get_related_authors":
                    result = await get_related_authors(session, arguments.get("author_id", ""))
                elif tool_name == "get_author_llms_txt":
                    result = await get_author_llms_txt(session, arguments.get("author_id", ""))
                else:
                    result = {
                        "status": "error",
                        "error": {"code": "unknown_tool", "message": f"Unknown tool: {tool_name}"},
                    }

            return JSONResponse(result)

        except SonexialError as e:
            return JSONResponse(e.to_response().model_dump(), status_code=404 if "not_found" in e.code else 400)
        except Exception as e:
            logger.error(f"Error processing tool call: {str(e)}")
            return JSONResponse(
                {"status": "error", "error": {"code": "internal_error", "message": str(e)}},
                status_code=500,
            )

    async def debug_tools(request: Request) -> JSONResponse:
        """Debug endpoint listing available tools (only in development)."""
        settings = get_settings()
        if not settings.is_development:
            return JSONResponse({"error": "Not available in this environment"}, status_code=404)

        return JSONResponse({
            "tools": [
                {"name": "ping", "description": "Health check"},
                {"name": "search_authors", "description": "Search for authors"},
                {"name": "get_author", "description": "Get author profile"},
                {"name": "list_books", "description": "List books by author"},
                {"name": "get_book", "description": "Get book details"},
                {"name": "search_lore", "description": "Search lore entries"},
                {"name": "get_related_authors", "description": "Find related authors"},
                {"name": "get_author_llms_txt", "description": "Get author llms.txt"},
            ]
        })

    routes = [
        Route("/healthz", healthz, methods=["GET"]),
        Route("/mcp", mcp_endpoint, methods=["POST"]),
        Route("/debug/tools", debug_tools, methods=["GET"]),
    ]

    app = Starlette(routes=routes, middleware=middleware)
    return app


async def run_http():
    """Run the MCP server using HTTP transport."""
    settings = get_settings()

    logger.info("Starting MCP server in HTTP mode...")

    # Initialize database
    await init_db()
    logger.info("Database initialized.")

    app = create_http_app()

    config = uvicorn.Config(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
    server = uvicorn.Server(config)

    logger.info(f"HTTP server listening on {settings.host}:{settings.port}")
    logger.info(f"Auth: {'disabled' if settings.auth_disabled else 'enabled'}")

    await server.serve()
