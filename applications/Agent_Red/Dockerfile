# Agent Red API container.

FROM acragentredeastus.azurecr.io/python:3.12-slim-bookworm

LABEL maintainer="Remaker Digital <dev@remakerdigital.com>"
LABEL project="Agent Red Customer Experience"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ARG BUILD_VERSION=unknown
RUN echo "build-version=${BUILD_VERSION}" > /tmp/.build-version

COPY src/ ./src/
COPY config/ ./config/
COPY admin/shopify/dist/ ./admin/shopify/dist/
COPY admin/standalone/dist/ ./admin/standalone/dist/
COPY admin/provider/dist/ ./admin/provider/dist/
COPY widget/dist/ ./widget/dist/
COPY docs-site/docs/ ./docs-site/docs/

RUN groupadd --gid 1000 agentred \
    && useradd --uid 1000 --gid agentred --shell /bin/sh --no-create-home agentred \
    && chown -R agentred:agentred /app

USER agentred
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5).read()"]

ENTRYPOINT ["tini", "--"]
CMD ["sh", "-c", "export INTERNAL_VERIFICATION_SECRET=${INTERNAL_VERIFICATION_SECRET:-$(python -c 'import secrets; print(secrets.token_hex(32))')} && exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info --no-server-header"]
