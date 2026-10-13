"""Health check tool."""

from ..schemas import PingResponse


def ping() -> dict:
    """Health check tool. Returns service status and version."""
    response = PingResponse()
    return response.model_dump()
