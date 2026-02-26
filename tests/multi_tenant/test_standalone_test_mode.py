"""Tests for test mode — config field, conversation tagging, analytics filtering.

WI #248: Test mode E2E validation in standalone admin.

Covers:
    - PUT  /api/config  with test_mode_enabled field (save to draft)
    - GET  /api/config  reads test_mode_enabled back
    - GET  /api/admin/analytics/summary?is_test_mode=true  (filter parameter)
    - GET  /api/admin/analytics/summary?is_test_mode=false (exclude test)
    - Conversation repo: is_test_mode flag on documents
    - Analytics repo: count_by_status respects is_test_mode filter

Architecture:
    Uses FastAPI test client with dependency overrides (same pattern as
    test_config_api_activation.py and test_admin_analytics_api.py).
    Mocks Cosmos DB repositories to isolate test mode logic.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.middleware import get_tenant_context


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-testmode-001"


def _make_context(
    tenant_id: str = TENANT_ID,
    tier: TenantTier = TenantTier.STARTER,
) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=tier,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


# ---------------------------------------------------------------------------
# Config API tests — test_mode_enabled field
# ---------------------------------------------------------------------------


class TestTestModeConfigField:
    """Verify test_mode_enabled can be saved and read via the config API.

    Uses the same patching pattern as test_config_api_activation.py:
    patch the module-level get_activation_service / get_config_processor
    singletons in tenant_config_api.
    """

    def test_save_test_mode_enabled_true(self) -> None:
        """PUT /api/config with test_mode_enabled=true should save to draft."""
        from src.multi_tenant.activation_service import DraftSaveResult
        from src.multi_tenant.tenant_config_api import router

        mock_svc = AsyncMock()
        mock_svc.save_draft = AsyncMock(return_value=DraftSaveResult(
            success=True,
            version=2,
            changes={"test_mode_enabled": True},
        ))
        mock_svc.get_draft_state = AsyncMock(return_value=MagicMock(
            has_pending_changes=False,
        ))

        mock_proc = AsyncMock()

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_tenant_context] = lambda: _make_context()

        with (
            patch(
                "src.multi_tenant.tenant_config_api.get_activation_service",
                return_value=mock_svc,
            ),
            patch(
                "src.multi_tenant.tenant_config_api.get_config_processor",
                return_value=mock_proc,
            ),
        ):
            client = TestClient(app)
            resp = client.put(
                "/api/config",
                json={"fields": {"test_mode_enabled": True}},
                headers={"X-API-Key": "test-key"},
            )

        assert resp.status_code == 200
        # Verify draft was saved with the test_mode_enabled field
        mock_svc.save_draft.assert_called_once()
        call_kwargs = mock_svc.save_draft.call_args[1]
        # save_draft(tenant_id=..., tier=..., changes={...})
        assert call_kwargs["changes"].get("test_mode_enabled") is True

        app.dependency_overrides.clear()

    def test_read_test_mode_enabled(self) -> None:
        """GET /api/config returns test_mode_enabled in the config payload."""
        from src.multi_tenant.tenant_config_processor import ConfigReadResult
        from src.multi_tenant.tenant_config_api import router

        mock_proc = AsyncMock()
        mock_proc.get_config = AsyncMock(return_value=ConfigReadResult(
            tenant_id=TENANT_ID,
            tier="starter",
            config={
                "test_mode_enabled": True,
                "brand_name": "Test Store",
            },
            preferences={},
            version=1,
            state="active",
        ))

        mock_svc = AsyncMock()

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_tenant_context] = lambda: _make_context()

        with (
            patch(
                "src.multi_tenant.tenant_config_api.get_activation_service",
                return_value=mock_svc,
            ),
            patch(
                "src.multi_tenant.tenant_config_api.get_config_processor",
                return_value=mock_proc,
            ),
        ):
            client = TestClient(app)
            resp = client.get(
                "/api/config",
                headers={"X-API-Key": "test-key"},
            )

        assert resp.status_code == 200
        data = resp.json()
        config = data.get("config", {})
        assert config.get("test_mode_enabled") is True

        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Analytics API tests — is_test_mode query parameter
# ---------------------------------------------------------------------------


class TestTestModeAnalyticsFilter:
    """Verify analytics endpoints respect the is_test_mode filter parameter.

    Uses configure_admin_analytics_services() to inject a mock repo,
    matching the pattern in test_admin_analytics_api.py. The router prefix
    is /api/analytics (not /api/admin/analytics).
    """

    def _make_client(self, mock_repo: Any) -> TestClient:
        """Build a TestClient with mock repo injected."""
        from src.multi_tenant.admin_analytics_api import (
            router,
            configure_admin_analytics_services,
        )

        configure_admin_analytics_services(mock_repo)

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_tenant_context] = lambda: _make_context()
        return TestClient(app)

    def _mock_repo(self) -> AsyncMock:
        """Build a mock ConversationRepository with canned data."""
        repo = AsyncMock()
        repo.aggregate_metrics = AsyncMock(return_value={
            "total": 5, "billable": 5, "avg_turns": 3.0,
            "avg_messages": 6.0, "escalated": 0,
            "critic_passed": 5, "critic_failed": 0,
        })
        repo.count_by_status = AsyncMock(return_value=[
            {"status": "ended", "count": 5},
        ])
        repo.count_fcr = AsyncMock(return_value={
            "resolved_count": 0, "fcr_count": 0, "fcr_rate": 0.0,
        })
        return repo

    def test_summary_filters_test_mode_true(self) -> None:
        """GET /api/analytics/summary?is_test_mode=true passes filter to repo."""
        mock_repo = self._mock_repo()
        client = self._make_client(mock_repo)

        resp = client.get("/api/analytics/summary?is_test_mode=true")

        assert resp.status_code == 200
        mock_repo.aggregate_metrics.assert_called_once()
        call_kwargs = mock_repo.aggregate_metrics.call_args[1]
        assert call_kwargs.get("is_test_mode") is True

    def test_summary_filters_test_mode_false(self) -> None:
        """GET /api/analytics/summary?is_test_mode=false excludes test convos."""
        mock_repo = self._mock_repo()
        client = self._make_client(mock_repo)

        resp = client.get("/api/analytics/summary?is_test_mode=false")

        assert resp.status_code == 200
        call_kwargs = mock_repo.aggregate_metrics.call_args[1]
        assert call_kwargs.get("is_test_mode") is False

    def test_summary_no_filter_returns_all(self) -> None:
        """GET /api/analytics/summary without is_test_mode returns all convos."""
        mock_repo = self._mock_repo()
        client = self._make_client(mock_repo)

        resp = client.get("/api/analytics/summary")

        assert resp.status_code == 200
        call_kwargs = mock_repo.aggregate_metrics.call_args[1]
        assert call_kwargs.get("is_test_mode") is None


# ---------------------------------------------------------------------------
# Conversation repository tests — is_test_mode field on documents
# ---------------------------------------------------------------------------


class TestTestModeConversationTagging:
    """Verify conversation documents respect the is_test_mode field."""

    @pytest.mark.asyncio
    async def test_count_by_status_filters_test_mode(self) -> None:
        """count_by_status with is_test_mode=True adds SQL filter."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository.__new__(ConversationRepository)
        # Mock the query method
        repo.query = AsyncMock(return_value=[{"status": "resolved", "count": 3}])

        result = await repo.count_by_status(
            tenant_id=TENANT_ID,
            since="2026-01-01T00:00:00Z",
            is_test_mode=True,
        )

        # Verify the query included the test mode filter
        call_args = repo.query.call_args
        query_text = call_args[0][1]  # second positional arg is the query
        assert "is_test_mode = true" in query_text

    @pytest.mark.asyncio
    async def test_count_by_status_excludes_test_mode(self) -> None:
        """count_by_status with is_test_mode=False excludes test conversations."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository.__new__(ConversationRepository)
        repo.query = AsyncMock(return_value=[{"status": "resolved", "count": 10}])

        result = await repo.count_by_status(
            tenant_id=TENANT_ID,
            since="2026-01-01T00:00:00Z",
            is_test_mode=False,
        )

        call_args = repo.query.call_args
        query_text = call_args[0][1]
        assert "is_test_mode = false" in query_text

    @pytest.mark.asyncio
    async def test_count_by_status_no_filter(self) -> None:
        """count_by_status with is_test_mode=None does not filter."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository.__new__(ConversationRepository)
        repo.query = AsyncMock(return_value=[{"status": "resolved", "count": 15}])

        result = await repo.count_by_status(
            tenant_id=TENANT_ID,
            since="2026-01-01T00:00:00Z",
            is_test_mode=None,
        )

        call_args = repo.query.call_args
        query_text = call_args[0][1]
        assert "is_test_mode" not in query_text

    @pytest.mark.asyncio
    async def test_aggregate_metrics_filters_test_mode(self) -> None:
        """aggregate_metrics with is_test_mode=True adds SQL filter."""
        from src.multi_tenant.repositories.conversation import ConversationRepository

        repo = ConversationRepository.__new__(ConversationRepository)
        repo.query = AsyncMock(return_value=[{
            "total": 5, "billable": 0, "escalated": 0,
            "avg_turns": 3.0, "avg_messages": 6.0,
        }])

        result = await repo.aggregate_metrics(
            tenant_id=TENANT_ID,
            since="2026-01-01T00:00:00Z",
            is_test_mode=True,
        )

        call_args = repo.query.call_args
        query_text = call_args[0][1]
        assert "is_test_mode = true" in query_text


# ---------------------------------------------------------------------------
# Conversation schema — is_test_mode field definition
# ---------------------------------------------------------------------------


class TestTestModeConversationSchema:
    """Verify the Conversation schema includes is_test_mode field."""

    def test_conversation_has_test_mode_field(self) -> None:
        """ConversationDocument model has is_test_mode field defaulting to False."""
        from src.multi_tenant.cosmos_schema import ConversationDocument

        convo = ConversationDocument(
            id="test-convo-1",
            tenant_id=TENANT_ID,
            conversation_id="test-convo-1",
            status="active",
            started_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:00:00Z",
        )
        assert convo.is_test_mode is False

    def test_conversation_test_mode_true(self) -> None:
        """ConversationDocument model accepts is_test_mode=True."""
        from src.multi_tenant.cosmos_schema import ConversationDocument

        convo = ConversationDocument(
            id="test-convo-2",
            tenant_id=TENANT_ID,
            conversation_id="test-convo-2",
            status="active",
            started_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:00:00Z",
            is_test_mode=True,
        )
        assert convo.is_test_mode is True


# ---------------------------------------------------------------------------
# Fields schema — test_mode_enabled field definition
# ---------------------------------------------------------------------------


class TestTestModeFieldsSchema:
    """Verify test_mode_enabled is defined in the fields.yaml schema."""

    def test_test_mode_field_exists_in_schema(self) -> None:
        """test_mode_enabled field is present in fields.yaml."""
        from pathlib import Path
        import yaml

        fields_path = Path(__file__).parent.parent.parent / "src" / "multi_tenant" / "schema" / "fields.yaml"
        with open(fields_path) as f:
            data = yaml.safe_load(f)

        # fields.yaml uses a flat list under "fields:" key
        all_fields = [f["field_name"] for f in data.get("fields", [])]
        assert "test_mode_enabled" in all_fields

    def test_test_mode_field_is_boolean(self) -> None:
        """test_mode_enabled field is type boolean."""
        from pathlib import Path
        import yaml

        fields_path = Path(__file__).parent.parent.parent / "src" / "multi_tenant" / "schema" / "fields.yaml"
        with open(fields_path) as f:
            data = yaml.safe_load(f)

        test_mode_field = None
        for field in data.get("fields", []):
            if field["field_name"] == "test_mode_enabled":
                test_mode_field = field
                break

        assert test_mode_field is not None
        assert test_mode_field["field_type"] == "boolean"
        assert test_mode_field["platform_default"] is False

    def test_test_mode_available_to_all_tiers(self) -> None:
        """test_mode_enabled is tier_gate=all (available to Starter+)."""
        from pathlib import Path
        import yaml

        fields_path = Path(__file__).parent.parent.parent / "src" / "multi_tenant" / "schema" / "fields.yaml"
        with open(fields_path) as f:
            data = yaml.safe_load(f)

        test_mode_field = None
        for field in data.get("fields", []):
            if field["field_name"] == "test_mode_enabled":
                test_mode_field = field
                break

        assert test_mode_field is not None
        assert test_mode_field["tier_gate"] == "all"
