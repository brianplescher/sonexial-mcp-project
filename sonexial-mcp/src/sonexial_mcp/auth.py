"""Authentication middleware and utilities."""

import hmac
from typing import Optional

from .config import get_settings
from .errors import AuthenticationError
from .logging import get_logger

logger = get_logger("auth")


def verify_api_key(authorization: Optional[str]) -> bool:
    """Verify the bearer token from the Authorization header."""
    settings = get_settings()

    # If auth is disabled, always allow
    if settings.auth_disabled:
        return True

    if not authorization:
        raise AuthenticationError("Missing Authorization header.")

    # Extract bearer token
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization header format. Use: Bearer <token>")

    token = parts[1].strip()
    if not hmac.compare_digest(token.encode(), settings.api_key.encode()):
        raise AuthenticationError("Invalid API key.")

    return True


def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    settings = get_settings()
    return not settings.auth_disabled
