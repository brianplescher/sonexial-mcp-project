# Sonexial Author MCP

A Model Context Protocol (MCP) server that exposes structured indie-author data as AI-callable tools and resources.

## Why Sonexial MCP Matters

Sonexial moves indie authors from passive web pages into proactive, queryable AI entities. This MCP server allows AI assistants, agents, search engines, and developer tools to retrieve structured author, book, trope, and lore data through a standardized protocol.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  AI Client      │────▶│  MCP Server      │────▶│  Database   │
│  (Claude, etc.) │     │  (stdio or HTTP) │     │  (SQLite/   │
└─────────────────┘     └──────────────────┘     │   Postgres) │
                                                  └─────────────┘
```

### Components
- **MCP Server**: Exposes tools and resources via stdio or HTTP transport
- **Database Layer**: SQLAlchemy 2.x with SQLite (dev) or PostgreSQL (prod)
- **Tool Layer**: Implements search, retrieval, and relationship queries
- **Auth Layer**: Bearer token authentication for HTTP mode

## Quick Start

### Prerequisites
- Python 3.11+
- pip or poetry

### Local Development

```bash
# Clone and enter directory
cd sonexial-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Seed the database
python -m sonexial_mcp.seed

# Run in stdio mode (for local MCP clients)
python -m sonexial_mcp.cli --transport stdio

# Run in HTTP mode (for remote clients)
python -m sonexial_mcp.cli --transport http
```

### Docker

```bash
docker compose up --build
```

The server will be available at `http://localhost:8080`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SONEXIAL_MCP_ENV` | `development` | Environment (development/staging/production) |
| `SONEXIAL_MCP_HOST` | `0.0.0.0` | HTTP host |
| `SONEXIAL_MCP_PORT` | `8080` | HTTP port |
| `DATABASE_URL` | `sqlite:///./sonexial.db` | Database connection URL |
| `SONEXIAL_MCP_API_KEY` | (required for HTTP) | Bearer token for auth |
| `AUTH_DISABLED` | `true` | Disable auth (dev only) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

## MCP Tools

### ping
Health check. Returns service status and version.

### search_authors
Search for authors by query, genre, tropes, and verification status.

**Input:**
```json
{
  "query": "cyberpunk",
  "genre": "cyberpunk",
  "tropes": ["found-family"],
  "verified_only": false,
  "limit": 10
}
```

### get_author
Get full author profile by ID.

**Input:**
```json
{
  "author_id": "sonexial:author:a1b2c3d4"
}
```

### list_books
List all books by an author.

**Input:**
```json
{
  "author_id": "sonexial:author:a1b2c3d4"
}
```

### get_book
Get book details by ID.

**Input:**
```json
{
  "book_id": "sonexial:book:e5f6g7h8"
}
```

### search_lore
Search lore entries by keyword.

**Input:**
```json
{
  "query": "dragon",
  "author_id": null,
  "book_id": null,
  "category": "character",
  "limit": 10
}
```

### get_related_authors
Find authors related to a given author.

**Input:**
```json
{
  "author_id": "sonexial:author:a1b2c3d4"
}
```

### get_author_llms_txt
Get a clean Markdown summary of an author, suitable for AI consumption.

**Input:**
```json
{
  "author_id": "sonexial:author:a1b2c3d4"
}
```

## MCP Client Configuration

### Claude Desktop (stdio)

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "sonexial-authors": {
      "command": "python",
      "args": ["-m", "sonexial_mcp.cli", "--transport", "stdio"],
      "cwd": "/path/to/sonexial-mcp"
    }
  }
}
```

### Remote HTTP Client

```json
{
  "mcpServers": {
    "sonexial-authors": {
      "url": "https://mcp.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_tools.py
```

## Project Structure

```
sonexial-mcp/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── Caddyfile.example
├── src/
│   └── sonexial_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── seed.py
│       ├── auth.py
│       ├── logging.py
│       ├── errors.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── authors.py
│       │   ├── books.py
│       │   ├── lore.py
│       │   └── health.py
│       ├── transports/
│       │   ├── __init__.py
│       │   ├── stdio.py
│       │   └── http.py
│       └── cli.py
├── seed_data/
│   ├── authors.json
│   ├── books.json
│   └── lore.json
├── tests/
│   ├── test_tools.py
│   └── test_server.py
├── scripts/
│   ├── seed.py
│   ├── run_stdio.sh
│   └── run_http.sh
└── deploy/
    ├── README.md
    └── systemd/
        └── sonexial-mcp.service.example
```

## Roadmap

- [ ] Vector search for lore entries (pgvector)
- [ ] Full-text search with PostgreSQL
- [ ] Author verification workflow
- [ ] Webhook notifications for data changes
- [ ] Rate limiting and quotas
- [ ] MCP resources (sonexial://authors, etc.)
- [ ] Streaming responses for large result sets
- [ ] Multi-tenant support
- [ ] Admin API for author self-service

## License

Proprietary - Sonexial Labs. All rights reserved.
