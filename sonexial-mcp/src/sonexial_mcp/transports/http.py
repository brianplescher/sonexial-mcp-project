"""Streamable HTTP transport for remote MCP clients.

Serves the real MCP protocol (JSON-RPC over HTTP) via the SDK's
StreamableHTTPSessionManager, mounted at /mcp. Stateless mode: each request is
self-contained, so there are no sessions to pin to one process.

Only /mcp requires a bearer token. /healthz stays open for load balancers and
the Docker healthcheck.
"""

from contextlib import asynccontextmanager

import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from ..auth import verify_api_key, is_auth_enabled
from ..config import get_settings
from ..database import init_db
from ..errors import AuthenticationError
from ..logging import get_logger
from ..server import create_server

logger = get_logger("transports.http")

MCP_PATH = "/mcp"


class BearerAuthMiddleware:
    """Pure ASGI middleware. Rejects /mcp requests without a valid bearer token."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == MCP_PATH:
            # Mount("/mcp") answers /mcp with a 307 to /mcp/. Normalize here so POSTs
            # are served directly and never rely on a redirect keeping the auth header.
            scope = {**scope, "path": MCP_PATH + "/"}

        if scope["type"] == "http" and scope["path"].startswith(MCP_PATH) and is_auth_enabled():
            header = None
            for name, value in scope.get("headers", []):
                if name == b"authorization":
                    header = value.decode("latin-1")
                    break
            try:
                verify_api_key(header)
            except AuthenticationError as e:
                response = JSONResponse(
                    e.to_response().model_dump(),
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


def create_http_app() -> Starlette:
    """Build the ASGI app: MCP at /mcp, health at /healthz."""
    settings = get_settings()

    session_manager = StreamableHTTPSessionManager(
        app=create_server(),
        stateless=True,
        json_response=True,
        security_settings=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=settings.allowed_hosts_list,
        ),
    )

    async def handle_mcp(scope, receive, send):
        await session_manager.handle_request(scope, receive, send)

    async def healthz(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok", "service": "sonexial-author-mcp", "version": "0.1.0"})

    @asynccontextmanager
    async def lifespan(app):
        await init_db()
        async with session_manager.run():
            logger.info("MCP session manager running (stateless streamable HTTP).")
            yield

    middleware = [
        Middleware(BearerAuthMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            # Credentials are not needed (bearer tokens, not cookies) and are unsafe with wildcard origins.
            allow_credentials=False,
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        ),
    ]

    return Starlette(
        routes=[
            Route("/healthz", healthz, methods=["GET"]),
            Mount(MCP_PATH, app=handle_mcp),
        ],
        middleware=middleware,
        lifespan=lifespan,
    )


async def run_http():
    """Run the streamable HTTP server under uvicorn."""
    settings = get_settings()

    if not settings.auth_disabled and settings.api_key in ("", "change-me"):
        raise RuntimeError(
            "Refusing to start: SONEXIAL_MCP_API_KEY is unset or still the placeholder. "
            "Set a strong key, or set SONEXIAL_MCP_AUTH_DISABLED=true for local development only."
        )

    logger.info("Starting MCP server in HTTP mode...")
    logger.info(f"HTTP server listening on {settings.host}:{settings.port}{MCP_PATH}")
    logger.info(f"Auth: {'disabled' if settings.auth_disabled else 'enabled'}")

    config = uvicorn.Config(
        create_http_app(),
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        proxy_headers=True,
        forwarded_allow_ips="127.0.0.1",
    )
    await uvicorn.Server(config).serve()
