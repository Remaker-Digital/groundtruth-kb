"""SPEC-1833: Cosmos DB Health in Readiness Probe.

Provides a cached, timeout-protected Cosmos DB connectivity check
that reads a health_sentinel document from platform_config. Falls back
to listing containers if the sentinel document is missing.

Integrated into /ready via health.py.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Cache configuration
_CACHE_TTL_SECONDS = 10
_COSMOS_TIMEOUT_SECONDS = 3

# Module-level cache
_cached_result: dict[str, Any] | None = None
_cache_timestamp: float = 0.0


def _clear_cache() -> None:
    """Reset the cached result (for testing)."""
    global _cached_result, _cache_timestamp
    _cached_result = None
    _cache_timestamp = 0.0


def _get_platform_config_container() -> Any:
    """Get the platform_config container proxy from CosmosManager."""
    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.cosmos_schema import COLLECTION_PLATFORM_CONFIG

    manager = get_cosmos_manager()
    return manager.get_container(COLLECTION_PLATFORM_CONFIG)


def _get_database() -> Any:
    """Get the database proxy from CosmosManager (for fallback)."""
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    manager = get_cosmos_manager()
    return manager._database


async def check_cosmos_ready() -> dict[str, Any]:
    """Check Cosmos DB readiness by reading the health_sentinel document.

    Returns a dict with:
        - status: "healthy", "healthy_fallback", or "unhealthy"
        - latency_ms: round-trip time in milliseconds (when healthy)
        - error: error message (when unhealthy)

    Results are cached for 10 seconds to avoid hammering Cosmos on
    frequent /ready calls.
    """
    global _cached_result, _cache_timestamp

    # Return cached result if still fresh
    now = time.monotonic()
    if _cached_result is not None and (now - _cache_timestamp) < _CACHE_TTL_SECONDS:
        return _cached_result

    result = await _perform_check()

    # Cache the result
    _cached_result = result
    _cache_timestamp = time.monotonic()

    return result


async def _perform_check() -> dict[str, Any]:
    """Execute the actual Cosmos DB health check with timeout."""
    start = time.monotonic()

    try:
        result = await asyncio.wait_for(
            _read_sentinel(),
            timeout=_COSMOS_TIMEOUT_SECONDS,
        )
        return result
    except asyncio.TimeoutError:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning("Cosmos DB readiness check timed out after %sms", elapsed_ms)
        return {
            "status": "unhealthy",
            "error": f"Cosmos DB check timed out after {_COSMOS_TIMEOUT_SECONDS}s",
            "latency_ms": elapsed_ms,
        }
    except Exception as exc:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning("Cosmos DB readiness check failed: %s", exc)
        return {
            "status": "unhealthy",
            "error": str(exc),
            "latency_ms": elapsed_ms,
        }


async def _read_sentinel() -> dict[str, Any]:
    """Read the health_sentinel document from platform_config."""
    start = time.monotonic()

    try:
        container = _get_platform_config_container()
        await container.read_item(
            item="health_sentinel",
            partition_key="health_sentinel",
        )
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        return {
            "status": "healthy",
            "latency_ms": elapsed_ms,
        }
    except Exception as sentinel_err:
        # Sentinel not found or error — fall back to listing containers
        logger.debug("Sentinel read failed (%s), attempting fallback", sentinel_err)
        return await _fallback_check(start)


async def _fallback_check(start: float) -> dict[str, Any]:
    """Fallback: verify Cosmos connectivity by listing containers."""
    try:
        database = _get_database()
        # Iterate at least one container to confirm connectivity
        async for _ in database.list_containers(max_item_count=1):
            break
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        return {
            "status": "healthy_fallback",
            "latency_ms": elapsed_ms,
        }
    except Exception as fallback_err:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        return {
            "status": "unhealthy",
            "error": str(fallback_err),
            "latency_ms": elapsed_ms,
        }
