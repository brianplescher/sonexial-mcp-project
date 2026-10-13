"""Standard I/O transport for local MCP clients."""

import asyncio
from mcp.server.stdio import stdio_server
from ..server import create_server
from ..database import init_db
from ..logging import get_logger

logger = get_logger("transports.stdio")


async def run_stdio():
    """Run the MCP server using stdio transport."""
    logger.info("Starting MCP server in stdio mode...")

    # Initialize database
    await init_db()
    logger.info("Database initialized.")

    server = create_server()

    async with stdio_server() as (read_stream, write_stream):
        logger.info("stdio transport ready. Waiting for messages...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
