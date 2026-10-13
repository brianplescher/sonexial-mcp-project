FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY scripts/ scripts/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV SONEXIAL_MCP_ENV=production
ENV SONEXIAL_MCP_HOST=0.0.0.0
ENV SONEXIAL_MCP_PORT=8080
ENV DATABASE_URL=sqlite+aiosqlite:////app/data/sonexial.db

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# Default command: run in HTTP mode with seed
CMD ["python", "-m", "sonexial_mcp.cli", "--transport", "http", "--seed"]
