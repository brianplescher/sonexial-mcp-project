"""Tests for the MCP server."""

import pytest
from unittest.mock import MagicMock, patch


class TestServerCreation:
    """Test server creation and configuration."""

    def test_server_can_be_created(self):
        """Test that the server module can be imported."""
        from sonexial_mcp.server import create_server
        # Just verify it doesn't raise
        assert callable(create_server)

    def test_cli_module_importable(self):
        """Test that the CLI module can be imported."""
        from sonexial_mcp.cli import main
        assert callable(main)

    def test_database_module_importable(self):
        """Test that the database module can be imported."""
        from sonexial_mcp.database import Base, init_db
        assert Base is not None
        assert callable(init_db)

    def test_models_importable(self):
        """Test that all models can be imported."""
        from sonexial_mcp.models import Author, Book, LoreEntry, AuthorRelationship
        assert Author.__tablename__ == "authors"
        assert Book.__tablename__ == "books"
        assert LoreEntry.__tablename__ == "lore_entries"
        assert AuthorRelationship.__tablename__ == "author_relationships"


class TestHTTPApp:
    """Test HTTP application creation."""

    def test_http_app_creates(self):
        """Test that the HTTP app can be created."""
        with patch("sonexial_mcp.config.get_settings") as mock:
            settings = MagicMock()
            settings.env = "development"
            settings.host = "0.0.0.0"
            settings.port = 8080
            settings.auth_disabled = True
            settings.api_key = "test"
            settings.log_level = "INFO"
            settings.cors_origins = "*"
            settings.cors_origins_list = ["*"]
            settings.is_development = True
            settings.is_production = False
            mock.return_value = settings

            from sonexial_mcp.transports.http import create_http_app
            app = create_http_app()
            assert app is not None
