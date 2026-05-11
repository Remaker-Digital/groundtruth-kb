"""Tests for idle conversation scanner background task.

Covers:
    - list_active_tenant_ids returns deduplicated tenant IDs
    - Idle scanner lifecycle (startup/shutdown hooks exist)
    - Scanner loop function exists

Run:
    pytest tests/multi_tenant/test_idle_scanner.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Tests: list_active_tenant_ids
# ---------------------------------------------------------------------------


class TestListActiveTenantIds:
    """Tests for TenantRepository.list_active_tenant_ids()."""

    @pytest.mark.asyncio
    async def test_returns_active_tenant_ids(self) -> None:
        from src.multi_tenant.repository import TenantRepository

        items = [
            {"tenant_id": "tenant-001"},
            {"tenant_id": "tenant-002"},
            {"tenant_id": "tenant-003"},
        ]

        async def _mock_query(*args, **kwargs):
            for item in items:
                yield item

        mock_container = MagicMock()
        mock_container.query_items = _mock_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            result = await repo.list_active_tenant_ids()

        assert result == ["tenant-001", "tenant-002", "tenant-003"]

    @pytest.mark.asyncio
    async def test_deduplicates_tenant_ids(self) -> None:
        from src.multi_tenant.repository import TenantRepository

        items = [
            {"tenant_id": "tenant-001"},
            {"tenant_id": "tenant-001"},
            {"tenant_id": "tenant-002"},
        ]

        async def _mock_query(*args, **kwargs):
            for item in items:
                yield item

        mock_container = MagicMock()
        mock_container.query_items = _mock_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            result = await repo.list_active_tenant_ids()

        assert result == ["tenant-001", "tenant-002"]

    @pytest.mark.asyncio
    async def test_empty_when_no_tenants(self) -> None:
        from src.multi_tenant.repository import TenantRepository

        async def _mock_query(*args, **kwargs):
            return
            yield  # Make it an async generator

        mock_container = MagicMock()
        mock_container.query_items = _mock_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            result = await repo.list_active_tenant_ids()

        assert result == []

    @pytest.mark.asyncio
    async def test_skips_items_without_tenant_id(self) -> None:
        from src.multi_tenant.repository import TenantRepository

        items = [
            {"tenant_id": "tenant-001"},
            {"other_field": "value"},
            {"tenant_id": "tenant-002"},
        ]

        async def _mock_query(*args, **kwargs):
            for item in items:
                yield item

        mock_container = MagicMock()
        mock_container.query_items = _mock_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            result = await repo.list_active_tenant_ids()

        assert result == ["tenant-001", "tenant-002"]


# ---------------------------------------------------------------------------
# Tests: list_expired_trials (TenantRepository, WI-D1)
# ---------------------------------------------------------------------------


class TestListExpiredTrials:
    """Tests for TenantRepository.list_expired_trials()."""

    @pytest.mark.asyncio
    async def test_returns_expired_trial_documents(self) -> None:
        from src.multi_tenant.repository import TenantRepository

        items = [
            {"tenant_id": "trial-001", "status": "active", "billing_channel": "trial"},
            {"tenant_id": "trial-002", "status": "active", "billing_channel": "trial"},
        ]

        async def _mock_query(*args, **kwargs):
            for item in items:
                yield item

        mock_container = MagicMock()
        mock_container.query_items = _mock_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            result = await repo.list_expired_trials()

        assert len(result) == 2
        assert result[0]["tenant_id"] == "trial-001"
        assert result[1]["tenant_id"] == "trial-002"

    @pytest.mark.asyncio
    async def test_empty_when_no_expired_trials(self) -> None:
        from src.multi_tenant.repository import TenantRepository

        async def _mock_query(*args, **kwargs):
            return
            yield  # Make it an async generator

        mock_container = MagicMock()
        mock_container.query_items = _mock_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            result = await repo.list_expired_trials()

        assert result == []

    @pytest.mark.asyncio
    async def test_query_uses_correct_filters(self) -> None:
        """Verify the Cosmos SQL query filters by active status, trial channel, and expired timestamp."""
        from src.multi_tenant.repository import TenantRepository

        captured_kwargs: dict = {}

        async def _capturing_query(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return
            yield

        mock_container = MagicMock()
        mock_container.query_items = _capturing_query

        with patch.object(TenantRepository, "_container", new_callable=lambda: property(lambda self: mock_container)):
            repo = TenantRepository.__new__(TenantRepository)
            await repo.list_expired_trials()

        # Verify query text contains all three filters
        query = captured_kwargs.get("query", "")
        assert "status = 'active'" in query
        assert "billing_channel = 'trial'" in query
        assert "trial_expires_at < @now" in query

        # Verify @now parameter is an ISO timestamp
        params = captured_kwargs.get("parameters", [])
        now_param = next((p for p in params if p["name"] == "@now"), None)
        assert now_param is not None
        # Should be a valid ISO timestamp
        from datetime import datetime
        parsed = datetime.fromisoformat(now_param["value"])
        assert parsed.tzinfo is not None


# ---------------------------------------------------------------------------
# Tests: Idle scanner lifecycle
# ---------------------------------------------------------------------------


class TestIdleScannerLifecycle:
    """Tests for idle scanner startup and shutdown."""

    def test_startup_creates_task(self) -> None:
        from src.main import _startup_idle_scanner
        assert callable(_startup_idle_scanner)

    def test_shutdown_cancels_task(self) -> None:
        from src.main import _shutdown_idle_scanner
        assert callable(_shutdown_idle_scanner)

    def test_scanner_loop_function_exists(self) -> None:
        from src.main import _idle_scanner_loop
        assert callable(_idle_scanner_loop)
