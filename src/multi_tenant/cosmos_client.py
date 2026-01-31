"""
Cosmos DB async client manager.

Manages a singleton CosmosClient with connection pooling, retry
configuration, and health checks. All database access across the
application flows through this module.

Usage:
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    manager = get_cosmos_manager()
    container = manager.get_container("tenants")
    item = await container.read_item("id", partition_key="tenant-123")

Configuration (environment variables):
    COSMOS_DB_ENDPOINT    — Cosmos DB account endpoint URL
    COSMOS_DB_KEY         — Cosmos DB account key (or use Managed Identity)
    COSMOS_DB_DATABASE    — Database name (default: agent-red-prod)
    COSMOS_USE_MANAGED_ID — "true" to use Azure Managed Identity instead of key

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from src.multi_tenant.cosmos_schema import DATABASE_NAME, initialize_database

logger = logging.getLogger(__name__)


class CosmosManager:
    """Singleton manager for Cosmos DB async client and container access.

    Provides:
        - Lazy client initialization (connects on first use)
        - Container proxy caching (avoids repeated lookups)
        - Health check for readiness probes
        - Graceful shutdown

    Thread safety: CosmosClient is internally thread-safe. Container
    proxies are lightweight references, safe to cache and share.
    """

    def __init__(self) -> None:
        self._client: CosmosClient | None = None
        self._database: Any = None  # DatabaseProxy
        self._containers: dict[str, Any] = {}  # name -> ContainerProxy
        self._initialized: bool = False

    async def _ensure_client(self) -> None:
        """Lazy-initialize the Cosmos DB client and database reference."""
        if self._client is not None:
            return

        endpoint = os.environ.get("COSMOS_DB_ENDPOINT", "")
        use_managed_id = os.environ.get("COSMOS_USE_MANAGED_ID", "").lower() == "true"
        database_name = os.environ.get("COSMOS_DB_DATABASE", DATABASE_NAME)

        if not endpoint:
            raise RuntimeError(
                "COSMOS_DB_ENDPOINT is not set. Cannot connect to Cosmos DB."
            )

        if use_managed_id:
            from azure.identity.aio import DefaultAzureCredential
            credential = DefaultAzureCredential()
            logger.info("Cosmos DB: using Managed Identity authentication")
        else:
            credential = os.environ.get("COSMOS_DB_KEY", "")
            if not credential:
                raise RuntimeError(
                    "COSMOS_DB_KEY is not set and COSMOS_USE_MANAGED_ID is not enabled."
                )
            logger.info("Cosmos DB: using account key authentication")

        self._client = CosmosClient(
            url=endpoint,
            credential=credential,
            # Connection policy defaults are suitable for Serverless:
            # - Retry on 429 (throttling) with backoff
            # - Connection pooling via aiohttp session
        )

        self._database = self._client.get_database_client(database_name)
        logger.info("Cosmos DB client initialized: endpoint=%s db=%s", endpoint, database_name)

    async def initialize(self) -> dict[str, Any]:
        """Initialize the database and create all containers.

        Call once at application startup. Idempotent — safe to call
        multiple times.

        Returns:
            Dict with initialization results.
        """
        await self._ensure_client()
        assert self._client is not None
        result = await initialize_database(self._client)
        self._initialized = True
        return result

    def get_container(self, collection_name: str) -> Any:
        """Get a ContainerProxy for the named collection.

        Container proxies are cached for reuse. The proxy is a
        lightweight reference — no network call is made here.

        Args:
            collection_name: One of the COLLECTION_* constants from cosmos_schema.

        Returns:
            A ContainerProxy for the collection.

        Raises:
            RuntimeError: If the client has not been initialized.
        """
        if self._database is None:
            raise RuntimeError(
                "CosmosManager not initialized. Call await manager.initialize() first."
            )

        if collection_name not in self._containers:
            self._containers[collection_name] = self._database.get_container_client(
                collection_name
            )

        return self._containers[collection_name]

    async def health_check(self) -> dict[str, Any]:
        """Check Cosmos DB connectivity for readiness probes.

        Performs a lightweight read against the database to verify
        the connection is alive.

        Returns:
            Dict with health status: {"status": "healthy"/"unhealthy", "detail": ...}
        """
        try:
            await self._ensure_client()
            assert self._database is not None
            # Read database properties as a lightweight connectivity check
            await self._database.read()
            return {"status": "healthy", "detail": "Cosmos DB connection OK"}
        except CosmosHttpResponseError as exc:
            logger.warning("Cosmos DB health check failed: %s", exc.message)
            return {"status": "unhealthy", "detail": f"Cosmos DB error: {exc.status_code}"}
        except Exception as exc:
            logger.warning("Cosmos DB health check failed: %s", exc)
            return {"status": "unhealthy", "detail": str(exc)}

    async def close(self) -> None:
        """Close the Cosmos DB client and release resources.

        Call during application shutdown.
        """
        if self._client is not None:
            await self._client.close()
            self._client = None
            self._database = None
            self._containers.clear()
            self._initialized = False
            logger.info("Cosmos DB client closed")


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_manager: CosmosManager | None = None


def get_cosmos_manager() -> CosmosManager:
    """Get the singleton CosmosManager instance.

    Returns:
        The global CosmosManager. Call await manager.initialize()
        before first use.
    """
    global _manager
    if _manager is None:
        _manager = CosmosManager()
    return _manager
