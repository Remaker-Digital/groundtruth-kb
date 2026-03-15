"""Health and readiness endpoints for Agent Red Customer Experience.

Provides /health (liveness probe) and /ready (readiness probe) endpoints
used by Azure Container Apps for traffic management.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, Request

from src.multi_tenant.nats_isolation import get_nats_manager
from src.multi_tenant.pipeline_resilience import get_circuit_breaker_registry
from src.multi_tenant.tenant_secret_service import get_secret_service
from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer

logger = logging.getLogger(__name__)


def register_health_endpoints(app: FastAPI) -> None:
    """Register /health and /ready endpoints on the FastAPI app."""

    @app.get("/health", tags=["system"])
    async def health() -> dict:
        """Liveness probe — returns 200 if the process is running."""
        from src.multi_tenant.api_versioning import API_VERSION, PRODUCT_VERSION

        return {"status": "healthy", "version": API_VERSION, "product_version": PRODUCT_VERSION}

    @app.get("/ready", tags=["system"])
    async def ready() -> dict:
        """Readiness probe — returns 200 if the service can accept traffic.

        Checks NATS connectivity when the manager is initialized.
        """
        result: dict[str, Any] = {"status": "ready"}

        nats_mgr = get_nats_manager()
        if nats_mgr.is_connected:
            nats_health = await nats_mgr.check_health()
            result["nats"] = {
                "connected": nats_health.connected,
                "circuit_breaker": nats_health.circuit_breaker_state,
                "active_streams": nats_health.active_streams,
            }
        else:
            result["nats"] = {"connected": False}

        # Circuit breaker health for external dependencies (WI #46)
        cb_registry = get_circuit_breaker_registry()
        cb_summary = cb_registry.health_summary()
        if cb_summary:
            result["circuit_breakers"] = {
                name: state for name, state in cb_summary.items()
            }

        # Key Vault health (WI #29)
        secret_svc = get_secret_service()
        result["key_vault"] = await secret_svc.health_check()

        # Tenant usage monitor health (WI #51)
        from src.multi_tenant.tenant_usage_monitor import get_usage_monitor

        usage_monitor = get_usage_monitor()
        result["usage_monitor"] = usage_monitor.health_summary()

        # SSE connection manager health (WI #129)
        from src.chat.sse_manager import get_sse_manager

        sse_mgr = get_sse_manager()
        result["sse_connections"] = sse_mgr.health_summary()

        # SLA monitoring (WI #151)
        from src.multi_tenant.sla_monitoring import get_sla_monitor

        sla_monitor = get_sla_monitor()
        result["sla"] = sla_monitor.health_summary()

        # Data retention service health (WI #154)
        from src.multi_tenant.data_retention import get_retention_service

        retention_svc = get_retention_service()
        result["data_retention"] = {"configured": retention_svc is not None}

        # KB retrieval metrics (WI #213)
        kb_vectorizer = get_knowledge_vectorizer()
        if kb_vectorizer._configured:
            result["kb_retrieval"] = kb_vectorizer.metrics.summary()
        else:
            result["kb_retrieval"] = {"configured": False}

        # Semantic cache health (WI #223-225)
        from src.multi_tenant.semantic_cache import get_semantic_cache

        sem_cache = get_semantic_cache()
        result["semantic_cache"] = sem_cache.health()

        # AGNTCY SDK / SLIM transport health (SPEC-1524, SPEC-1780)
        from src.multi_tenant.agntcy_sdk_integration import get_sdk_status

        sdk_status = get_sdk_status()
        result["agntcy_sdk"] = sdk_status

        # SPEC-1802 / SPEC-1780: In deployed environments, /ready returns 503
        # when transport is not active. HTTP containers are failure mode, not ready.
        environment = os.environ.get("ENVIRONMENT", "development").lower()
        active_tier = sdk_status.get("active_tier", "http_failure_mode")
        if environment in ("staging", "production") and not sdk_status.get("transport_active"):
            from starlette.responses import JSONResponse

            result["status"] = "not_ready"
            result["transport_enforcement"] = (
                f"AGNTCY transport not active in {environment}. "
                f"Current tier: {active_tier}. "
                "SPEC-1802 requires SLIM or NATS transport for deployed environments."
            )
            return JSONResponse(status_code=503, content=result)

        # Cross-replica cache invalidation (SPEC-1757)
        from src.multi_tenant.cache_invalidation import is_configured as cache_invalidation_configured

        result["cache_invalidation"] = {"redis_pubsub": cache_invalidation_configured()}

        # API version (WI #140)
        from src.multi_tenant.api_versioning import API_VERSION

        result["version"] = API_VERSION

        return result

    @app.get("/health/metrics", tags=["system"])
    async def health_metrics(request: Request) -> dict:
        """SPEC-1760: Scaling metrics for monitoring at 680-tenant scale.

        Exposes internal resource counters useful for capacity planning and
        alerting. Authenticated: platform-admin only.

        Metrics returned:
        - active_sse_connections / global_sse_limit
        - rate_limit_shard_sizes (per-shard tenant counts)
        - tenant_meta_cache_size / cache_hit_rate
        - config_cache_ttl
        - pre_auth_tracker_count
        - tenant_lock_count
        - uptime_seconds
        - event_loop_lag_ms
        """
        import asyncio
        import time as _time

        from starlette.responses import JSONResponse

        # --- Auth gate: platform admin only ---
        # /health/* is auth-exempt at middleware level, so we must
        # authenticate the platform admin key directly here.
        api_key = request.headers.get("X-API-Key", "")
        if not api_key.startswith("ar_spa_"):
            return JSONResponse(
                status_code=403,
                content={"error": "Platform admin authentication required"},
            )
        try:
            from src.multi_tenant.auth import hash_api_key, SPA_API_KEY_PREFIX
            from src.multi_tenant.repositories.platform_admin import PlatformAdminRepository

            key_hash = hash_api_key(api_key)
            repo = PlatformAdminRepository()
            admin = await repo.find_by_api_key_hash(key_hash)
            if admin is None or not admin.get("is_active", False):
                return JSONResponse(
                    status_code=403,
                    content={"error": "Invalid platform admin key"},
                )
        except Exception:
            return JSONResponse(
                status_code=403,
                content={"error": "Platform admin authentication failed"},
            )

        metrics: dict[str, Any] = {}

        # SSE connections (SPEC-1756)
        from src.chat.sse_manager import get_sse_manager, GLOBAL_SSE_MAX_CONNECTIONS

        sse = get_sse_manager()
        metrics["active_sse_connections"] = sse.global_connection_count
        metrics["global_sse_limit"] = GLOBAL_SSE_MAX_CONNECTIONS
        metrics["sse_global_limit_reached"] = sse.is_global_limit_reached
        metrics["tenants_streaming"] = len(sse._connections)

        # Rate limit shard sizes (SPEC-1745)
        try:
            from src.multi_tenant.middleware import _tenant_meta_cache

            # Access shards through the middleware module
            rate_limit_shard_sizes: list[int] = []
            # Import is deferred — middleware may not have a running instance
            metrics["tenant_meta_cache_size"] = len(_tenant_meta_cache)
        except Exception:
            metrics["tenant_meta_cache_size"] = -1

        # Config cache TTL (SPEC-1748)
        from src.multi_tenant.config.cache import CACHE_TTL_SECONDS

        metrics["config_cache_ttl_seconds"] = CACHE_TTL_SECONDS

        # Pre-auth tracker count (SPEC-1758)
        from src.multi_tenant.security_hardening import (
            get_pre_auth_limiter,
            MAX_TRACKED_IPS,
        )

        limiter = get_pre_auth_limiter()
        metrics["pre_auth_tracker_count"] = limiter.tracker_count
        metrics["pre_auth_tracker_limit"] = MAX_TRACKED_IPS

        # Tenant QA lock count (SPEC-1759)
        from src.multi_tenant.admin_quick_action_api import (
            _tenant_qa_locks,
            MAX_TENANT_LOCKS,
        )

        metrics["tenant_lock_count"] = len(_tenant_qa_locks)
        metrics["tenant_lock_limit"] = MAX_TENANT_LOCKS

        # Uptime
        if not hasattr(health_metrics, "_start_time"):
            health_metrics._start_time = _time.monotonic()  # type: ignore[attr-defined]
        metrics["uptime_seconds"] = round(
            _time.monotonic() - health_metrics._start_time, 1  # type: ignore[attr-defined]
        )

        # Event loop lag — schedule a callback and measure delay
        loop = asyncio.get_event_loop()
        lag_start = loop.time()
        await asyncio.sleep(0)  # yield to event loop
        lag_ms = round((loop.time() - lag_start) * 1000, 2)
        metrics["event_loop_lag_ms"] = lag_ms

        # API version
        from src.multi_tenant.api_versioning import API_VERSION, PRODUCT_VERSION

        metrics["api_version"] = API_VERSION
        metrics["product_version"] = PRODUCT_VERSION

        return metrics
