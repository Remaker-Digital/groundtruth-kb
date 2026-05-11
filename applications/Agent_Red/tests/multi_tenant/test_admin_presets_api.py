"""Tests for Admin Presets API — G6 Vertical Template Starter Kits (SPEC-1878).

Covers:
    - GET /api/admin/presets — list presets
    - GET /api/admin/presets/{id} — get detail
    - GET /api/admin/presets/{id} — 404 for unknown
    - POST /api/admin/presets/{id}/apply — apply preset
    - POST /api/admin/presets/{id}/apply — 404 for unknown

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.admin_presets_api import router


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-preset-api-test-001"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_ctx() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        tier=TenantTier.STARTER,
        status=TenantStatus.ACTIVE,
    )


@pytest.fixture
def client() -> TestClient:
    """Create a test client with the presets router."""
    app = FastAPI()
    app.include_router(router)

    # Override tenant context dependency
    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = _make_ctx

    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/admin/presets
# ---------------------------------------------------------------------------


class TestListPresets:
    def test_list_returns_200(self, client: TestClient) -> None:
        resp = client.get("/api/admin/presets")
        assert resp.status_code == 200
        data = resp.json()
        assert "presets" in data
        assert "total_count" in data
        assert data["total_count"] == 4

    def test_list_contains_expected_ids(self, client: TestClient) -> None:
        resp = client.get("/api/admin/presets")
        ids = {p["id"] for p in resp.json()["presets"]}
        assert ids == {"knowledge_only", "returns_agent", "presales_copilot", "order_support"}

    def test_list_preset_metadata_shape(self, client: TestClient) -> None:
        resp = client.get("/api/admin/presets")
        for p in resp.json()["presets"]:
            assert "id" in p
            assert "display_name" in p
            assert "description" in p
            assert "icon" in p
            assert "quick_action_count" in p
            assert "article_count" in p


# ---------------------------------------------------------------------------
# GET /api/admin/presets/{preset_id}
# ---------------------------------------------------------------------------


class TestGetPreset:
    def test_get_known_preset(self, client: TestClient) -> None:
        resp = client.get("/api/admin/presets/returns_agent")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "returns_agent"
        assert "preferences" in data
        assert "quick_actions" in data

    def test_get_unknown_preset_404(self, client: TestClient) -> None:
        resp = client.get("/api/admin/presets/nonexistent")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/admin/presets/{preset_id}/apply
# ---------------------------------------------------------------------------


class TestApplyPreset:
    def test_apply_unknown_preset_404(self, client: TestClient) -> None:
        resp = client.post("/api/admin/presets/nonexistent/apply")
        assert resp.status_code == 404

    def test_apply_known_preset_returns_result(self, client: TestClient) -> None:
        """Mock the service layer and verify the response shape."""
        from src.presets.preset_service import ApplyResult

        mock_result = ApplyResult(
            draft_created=True,
            quick_actions_created=3,
            assignments_created=True,
            articles_created=2,
            agents_recommended=[{"agent_id": "sales", "tier_required": "professional"}],
        )

        with patch(
            "src.multi_tenant.admin_presets_api.get_preset_service",
        ) as mock_get_svc:
            mock_svc = MagicMock()
            mock_svc.apply_preset = AsyncMock(return_value=mock_result)
            mock_svc.get_preset.return_value = {"id": "returns_agent"}  # needed for 404 check
            mock_get_svc.return_value = mock_svc

            resp = client.post("/api/admin/presets/returns_agent/apply")
            assert resp.status_code == 200
            data = resp.json()
            assert data["draft_created"] is True
            assert data["quick_actions_created"] == 3
            assert data["assignments_created"] is True
            assert data["articles_created"] == 2
            assert len(data["agents_recommended"]) == 1
