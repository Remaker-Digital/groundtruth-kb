# Dockerfile — Agent Red Customer Experience API Server (Production)
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# Build:
#   docker build -t agentred-api:latest .
#
# Run:
#   docker run -p 8000:8000 \
#     -e AZURE_OPENAI_ENDPOINT=https://aoai-agentred-eastus2.openai.azure.com/ \
#     -e COSMOS_DB_ENDPOINT=https://cosmos-agentred-eastus2.documents.azure.com:443/ \
#     -e KEY_VAULT_URL=https://kv-agentred-eastus2.vault.azure.net/ \
#     agentred-api:latest

FROM python:3.12-slim

# --------------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------------
LABEL maintainer="Remaker Digital <dev@remakerdigital.com>"
LABEL project="Agent Red Customer Experience"
LABEL version="1.0.0"
LABEL copyright="© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved."

# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------
# Prevent .pyc files and enable unbuffered stdout/stderr for container logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# --------------------------------------------------------------------------
# System dependencies
# --------------------------------------------------------------------------
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# Python dependencies (cached layer — only rebuilds when requirements.txt changes)
# --------------------------------------------------------------------------
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------------------------
# Application source and configuration
# ARG+RUN pattern forces full cache invalidation for COPY below
# --------------------------------------------------------------------------
ARG BUILD_VERSION=unknown
RUN echo "build-version=${BUILD_VERSION}" > /tmp/.build-version
COPY src/ ./src/
COPY config/ ./config/

# --------------------------------------------------------------------------
# Admin SPAs (pre-built Vite output for embedded + standalone + provider admin)
# --------------------------------------------------------------------------
COPY admin/shopify/dist/ ./admin/shopify/dist/
COPY admin/standalone/dist/ ./admin/standalone/dist/
COPY admin/provider/dist/ ./admin/provider/dist/

# --------------------------------------------------------------------------
# Widget bundle (IIFE single-file for embedding via <script> tag)
# --------------------------------------------------------------------------
COPY widget/dist/ ./widget/dist/

# --------------------------------------------------------------------------
# Non-root user for security
# --------------------------------------------------------------------------
RUN groupadd --gid 1000 agentred \
    && useradd --uid 1000 --gid agentred --shell /bin/sh --no-create-home agentred \
    && chown -R agentred:agentred /app

USER agentred

# --------------------------------------------------------------------------
# Networking
# --------------------------------------------------------------------------
EXPOSE 8000

# --------------------------------------------------------------------------
# Health check — /health is the liveness probe endpoint
# --------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# --------------------------------------------------------------------------
# Entrypoint — tini ensures proper signal handling for PID 1
# --------------------------------------------------------------------------
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
