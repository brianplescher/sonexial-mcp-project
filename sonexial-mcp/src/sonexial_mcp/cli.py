"""Command-line interface for Sonexial Author MCP."""

import argparse
import asyncio
import sys

from .config import get_settings
from .logging import setup_logging, get_logger


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Sonexial Author MCP Server",
        prog="sonexial-mcp",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode: stdio for local clients, http for remote clients",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed the database before starting",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Override host for HTTP transport",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override port for HTTP transport",
    )

    args = parser.parse_args()

    # Setup logging
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = get_logger("cli")

    logger.info(f"Sonexial Author MCP v0.1.0")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Transport: {args.transport}")

    # Run
    async def _run():
        # Seed if requested
        if args.seed:
            from .seed import seed_database
            await seed_database()

        if args.transport == "stdio":
            from .transports.stdio import run_stdio
            await run_stdio()
        elif args.transport == "http":
            from .transports.http import run_http
            await run_http()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
