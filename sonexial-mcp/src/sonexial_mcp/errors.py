"""Structured error handling and error responses."""

from typing import Optional, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structured error detail."""
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    status: str = "error"
    error: ErrorDetail


class SonexialError(Exception):
    """Base exception for Sonexial MCP errors."""

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            error=ErrorDetail(
                code=self.code,
                message=self.message,
                details=self.details,
            )
        )


class NotFoundError(SonexialError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code=f"{resource}_not_found",
            message=f"No {resource} exists with identifier: {identifier}",
        )


class InvalidInputError(SonexialError):
    """Invalid input parameters."""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(
            code="invalid_input",
            message=message,
            details=details,
        )


class AuthenticationError(SonexialError):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid or missing API key."):
        super().__init__(
            code="authentication_failed",
            message=message,
        )


class DatabaseError(SonexialError):
    """Database operation failed."""

    def __init__(self, message: str = "A database error occurred."):
        super().__init__(
            code="database_error",
            message=message,
        )
