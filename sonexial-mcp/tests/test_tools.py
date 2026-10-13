"""Tests for MCP tool implementations."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Test the tool functions directly


@pytest.fixture
def mock_settings():
    """Mock settings for tests."""
    with patch("sonexial_mcp.config.get_settings") as mock:
        settings = MagicMock()
        settings.env = "development"
        settings.database_url = "sqlite+aiosqlite:///./test_sonexial.db"
        settings.auth_disabled = True
        settings.api_key = "test-key"
        settings.log_level = "DEBUG"
        settings.cors_origins = "*"
        settings.is_development = True
        settings.is_production = False
        settings.cors_origins_list = ["*"]
        mock.return_value = settings
        yield settings


class TestPing:
    """Test the ping tool."""

    def test_ping_returns_ok(self):
        from sonexial_mcp.tools.health import ping
        result = ping()
        assert result["status"] == "ok"
        assert result["service"] == "sonexial-author-mcp"
        assert result["version"] == "0.1.0"


class TestSchemas:
    """Test Pydantic schemas."""

    def test_ping_response_schema(self):
        from sonexial_mcp.schemas import PingResponse
        response = PingResponse()
        data = response.model_dump()
        assert data["status"] == "ok"
        assert data["service"] == "sonexial-author-mcp"

    def test_author_summary_schema(self):
        from sonexial_mcp.schemas import AuthorSummary
        summary = AuthorSummary(
            id="test-id",
            name="Test Author",
            slug="test-author",
            genres=["cyberpunk"],
            tropes=["found-family"],
            verification_status="verified_human",
        )
        data = summary.model_dump()
        assert data["name"] == "Test Author"
        assert "cyberpunk" in data["genres"]

    def test_error_response(self):
        from sonexial_mcp.errors import NotFoundError
        error = NotFoundError("author", "test-id-123")
        response = error.to_response()
        data = response.model_dump()
        assert data["status"] == "error"
        assert data["error"]["code"] == "author_not_found"
        assert "test-id-123" in data["error"]["message"]


class TestConfig:
    """Test configuration."""

    def test_settings_defaults(self, mock_settings):
        assert mock_settings.env == "development"
        assert mock_settings.auth_disabled is True

    def test_is_development(self, mock_settings):
        assert mock_settings.is_development is True
        assert mock_settings.is_production is False


class TestErrors:
    """Test error classes."""

    def test_not_found_error(self):
        from sonexial_mcp.errors import NotFoundError
        error = NotFoundError("book", "book-123")
        assert error.code == "book_not_found"
        assert "book-123" in error.message

    def test_invalid_input_error(self):
        from sonexial_mcp.errors import InvalidInputError
        error = InvalidInputError("Missing required field", field="author_id")
        assert error.code == "invalid_input"
        assert error.details["field"] == "author_id"

    def test_authentication_error(self):
        from sonexial_mcp.errors import AuthenticationError
        error = AuthenticationError()
        assert error.code == "authentication_failed"

    def test_database_error(self):
        from sonexial_mcp.errors import DatabaseError
        error = DatabaseError("Connection failed")
        assert error.code == "database_error"
        assert "Connection failed" in error.message


class TestAuth:
    """Test authentication."""

    def test_auth_disabled_allows_all(self, mock_settings):
        from sonexial_mcp.auth import verify_api_key
        # Should not raise when auth is disabled
        result = verify_api_key(None)
        assert result is True

    def test_auth_disabled_check(self, mock_settings):
        from sonexial_mcp.auth import is_auth_enabled
        assert is_auth_enabled() is False
