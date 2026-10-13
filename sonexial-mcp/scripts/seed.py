"""Standalone seed script."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sonexial_mcp.seed import seed_database
from sonexial_mcp.logging import setup_logging


def main():
    setup_logging("INFO")
    asyncio.run(seed_database())
    print("Database seeded successfully.")


if __name__ == "__main__":
    main()
