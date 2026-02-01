# Agent Red Customer Experience - Development Dockerfile
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

FROM python:3.12-slim AS base

LABEL maintainer="Remaker Digital <dev@remakerdigital.com>"
LABEL project="Agent Red Customer Experience"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt* ./
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application source
COPY src/ ./src/

# Expose default service port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command (override in docker-compose for development)
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
