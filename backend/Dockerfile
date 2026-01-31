# ============================================
# Base stage - common dependencies
# ============================================
FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# ============================================
# Development stage
# ============================================
FROM base AS development

# Install all dependencies including dev
RUN uv sync --no-cache

# Copy source code
COPY . .

# Create data directory
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Production stage
# ============================================
FROM base AS production

# Install only production dependencies
RUN uv sync --no-cache --no-dev

# Copy source code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
