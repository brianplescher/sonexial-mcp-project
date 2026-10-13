#!/bin/bash
# Run MCP server in stdio mode
set -e
cd "$(dirname "$0")/.."
exec python -m sonexial_mcp.cli --transport stdio "$@"
