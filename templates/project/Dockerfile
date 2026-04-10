# {{PROJECT_NAME}} Container Image
# Multi-stage build for production Python applications.
#
# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
# All rights reserved.

# --- Stage 1: Build dependencies ---
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production image ---
FROM python:3.12-slim AS production

LABEL maintainer="{{OWNER}}"
LABEL project="{{PROJECT_NAME}}"

# Security: run as non-root user.
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Copy installed dependencies from builder stage.
COPY --from=builder /install /usr/local

# Copy application source.
COPY src/ ./src/
COPY pyproject.toml ./

# Set ownership.
RUN chown -R app:app /app

USER app

# Default port.
EXPOSE 8000

# Health check.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Entry point.
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
