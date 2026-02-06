# Project Chimera - Dockerfile
# Production-grade containerization for autonomous influencer system

# ==================== Build Stage ====================
FROM python:3.12-slim as builder

# Install UV for fast dependency management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first (cache optimization)
COPY pyproject.toml ./

# Install dependencies in virtual environment
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync --locked --no-dev

# ==================== Runtime Stage ====================
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 chimera && \
    mkdir -p /app && \
    chown -R chimera:chimera /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=chimera:chimera /app/.venv /app/.venv

# Copy application code
COPY --chown=chimera:chimera . /app/

# Switch to non-root user
USER chimera

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Expose ports
# 8000 - Orchestrator API
# 9090 - Prometheus metrics
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (override in docker-compose)
CMD ["python", "-m", "uvicorn", "chimera.services.orchestrator:app", "--host", "0.0.0.0", "--port", "8000"]
