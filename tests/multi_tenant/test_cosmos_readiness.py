"""Tests for SPEC-1833: Cosmos DB Health in Readiness Probe.

Verifies that /ready includes an explicit Cosmos DB connectivity check
via a health_sentinel document pattern with caching and timeout.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCosmosReadinessProbe:
    """SPEC-1833: /ready must include Cosmos DB connectivity check."""

    @pytest.mark.asyncio
    async def test_ready_includes_cosmos_db_status_healthy(self):
        """TEST-10438: When Cosmos is reachable, cosmos_db.status = healthy."""
        from src.multi_tenant.cosmos_readiness import check_cosmos_ready

        mock_container = AsyncMock()
        mock_container.read_item.return_value = {
            "id": "health_sentinel",
            "status": "ok",
            "updated_at": "2026-03-16T00:00:00Z",
        }

        with patch(
            "src.multi_tenant.cosmos_readiness._get_platform_config_container",
            return_value=mock_container,
        ):
            result = await check_cosmos_ready()

        assert result["status"] == "healthy"
        assert "latency_ms" in result
        assert result["latency_ms"] >= 0

    @pytest.mark.asyncio
    async def test_ready_includes_cosmos_db_status_unhealthy(self):
        """TEST-10439: When Cosmos is unreachable, cosmos_db.status = unhealthy and ready=false."""
        from src.multi_tenant.cosmos_readiness import check_cosmos_ready

        mock_container = AsyncMock()
        mock_container.read_item.side_effect = Exception("Connection refused")

        with patch(
            "src.multi_tenant.cosmos_readiness._get_platform_config_container",
            return_value=mock_container,
        ):
            result = await check_cosmos_ready()

        assert result["status"] == "unhealthy"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_cosmos_check_cached_for_10_seconds(self):
        """TEST-10440: Repeated /ready calls within 10s use cached Cosmos result."""
        from src.multi_tenant.cosmos_readiness import check_cosmos_ready, _clear_cache

        _clear_cache()  # Reset any prior state

        mock_container = AsyncMock()
        mock_container.read_item.return_value = {
            "id": "health_sentinel",
            "status": "ok",
            "updated_at": "2026-03-16T00:00:00Z",
        }

        with patch(
            "src.multi_tenant.cosmos_readiness._get_platform_config_container",
            return_value=mock_container,
        ):
            result1 = await check_cosmos_ready()
            result2 = await check_cosmos_ready()

        # Only one actual Cosmos call — second was cached
        assert mock_container.read_item.call_count == 1
        assert result1["status"] == "healthy"
        assert result2["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_cosmos_check_timeout_3_seconds(self):
        """SPEC-1833 req 2: Cosmos check has 3-second timeout."""
        from src.multi_tenant.cosmos_readiness import check_cosmos_ready, _clear_cache

        _clear_cache()

        mock_container = AsyncMock()

        async def slow_read(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate very slow Cosmos
            return {"id": "health_sentinel"}

        mock_container.read_item.side_effect = slow_read

        with patch(
            "src.multi_tenant.cosmos_readiness._get_platform_config_container",
            return_value=mock_container,
        ):
            start = time.monotonic()
            result = await check_cosmos_ready()
            elapsed = time.monotonic() - start

        assert result["status"] == "unhealthy"
        assert elapsed < 5  # Should timeout well before 5s

    @pytest.mark.asyncio
    async def test_fallback_to_list_containers_when_sentinel_missing(self):
        """SPEC-1833 req 6: Falls back to list_containers if sentinel missing."""
        from src.multi_tenant.cosmos_readiness import check_cosmos_ready, _clear_cache

        _clear_cache()

        mock_container = AsyncMock()
        # Sentinel not found
        mock_container.read_item.side_effect = Exception("NotFound")

        mock_database = AsyncMock()
        mock_database.list_containers.return_value = AsyncMock(
            __aiter__=AsyncMock(return_value=iter([{"id": "platform_config"}]))
        )

        with patch(
            "src.multi_tenant.cosmos_readiness._get_platform_config_container",
            return_value=mock_container,
        ), patch(
            "src.multi_tenant.cosmos_readiness._get_database",
            return_value=mock_database,
        ):
            result = await check_cosmos_ready()

        # Fallback should still report healthy if database is reachable
        assert result["status"] in ("healthy", "healthy_fallback")
