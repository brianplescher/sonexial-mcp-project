"""Pytest configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_settings_fixture():
    """Auto-mock settings for all tests."""
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
        settings.host = "0.0.0.0"
        settings.port = 8080
        mock.return_value = settings
        yield settings
