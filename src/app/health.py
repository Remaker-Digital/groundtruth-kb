"""Health and readiness endpoints for Agent Red Customer Experience.

Provides /health (liveness probe) and /ready (readiness probe) endpoints
used by Azure Container Apps for traffic management.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI

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

        # API version (WI #140)
        from src.multi_tenant.api_versioning import API_VERSION

        result["version"] = API_VERSION

        return result
