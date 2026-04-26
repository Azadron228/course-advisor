# Stage 1: Base image
FROM python:3.11-slim AS base

# Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Stage 2: Development target (hot reload, dev dependencies)
FROM base AS dev

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:${PATH}"

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies including dev ones
RUN uv sync --frozen

# Copy source code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start with reload enabled for development
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Builder for production
FROM base AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install only production dependencies
# --no-dev excludes dev dependencies
# --no-install-project skips installing the project itself as a package (optional)
RUN uv sync --frozen --no-dev --no-install-project

# Stage 4: Production (minimal runtime image)
FROM base AS prod

# Create a non-root user for security
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/sh appuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appgroup . .

# Ensure the alembic versions directory exists and is writable by appuser
# This is crucial for volume mounting and generating migrations on the host
RUN mkdir -p /app/alembic/versions && \
    chown -R appuser:appgroup /app/alembic/versions

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
