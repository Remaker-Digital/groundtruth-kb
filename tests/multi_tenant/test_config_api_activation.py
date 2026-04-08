"""Tests for config API activation endpoints — Save → Activate lifecycle.

Covers:
    - GET  /api/config/activation-status  (no changes, has changes)
    - GET  /api/config/draft              (no draft, with draft)
    - POST /api/config/draft/activate     (success, validation failure, no draft)
    - POST /api/config/draft/discard      (success, no draft)
    - POST /api/config/restore            (success, no previous)
    - PUT  /api/config                    (saves to draft, state=draft)
    - GET  /api/config?state=draft        (returns draft config)
    - POST /api/config/reset              (creates draft from defaults)
    - Auth enforcement                    (unauthenticated requests rejected)

Architecture:
    These tests use a lightweight FastAPI test client with dependency overrides
    rather than the full src.main app, isolating the config router and mocking
    both ActivationService and TenantConfigProcessor singletons.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.activation_service import (
    ActivationResult,
    DraftSaveResult,
    DraftState,
    RestoreResult,
)
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.tenant_config_api import router
from src.multi_tenant.tenant_config_processor import ConfigReadResult


# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------

TENANT_ID = "t-activation-001"
ACTIVE_ACTIVATED_AT = "2026-01-15T12:00:00+00:00"
DRAFT_ACTIVATED_AT = "2026-01-16T08:00:00+00:00"


def _make_context(
    tenant_id: str = TENANT_ID,
    tier: TenantTier = TenantTier.STARTER,
) -> TenantContext:
    """Build a minimal TenantContext for testing."""
    return TenantContext(
        tenant_id=tenant_id,
        tier=tier,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
        shop_domain=None,
        user_id=None,
        session_id=None,
    )


def _draft_state_no_changes(active_version: int = 1) -> DraftState:
    """DraftState with no pending changes."""
    return DraftState(
        has_pending_changes=False,
        active_version=active_version,
        active_activated_at=ACTIVE_ACTIVATED_AT,
        draft_version=None,
        changed_fields=[],
        draft_config={},
        active_config={},
    )


def _draft_state_with_changes(
    active_version: int = 1,
    draft_version: int = 2,
    changed_fields: list[str] | None = None,
    draft_config: dict[str, Any] | None = None,
    active_config: dict[str, Any] | None = None,
) -> DraftState:
    """DraftState with pending draft changes."""
    fields = changed_fields or ["brand_name"]
    return DraftState(
        has_pending_changes=True,
        active_version=active_version,
        active_activated_at=ACTIVE_ACTIVATED_AT,
        draft_version=draft_version,
        changed_fields=fields,
        draft_config=draft_config or {"brand_name": "New Brand"},
        active_config=active_config or {"brand_name": "Old Brand"},
    )


def _config_read_result(
    version: int = 1,
    config: dict[str, Any] | None = None,
) -> ConfigReadResult:
    """Build a ConfigReadResult for mocking get_config."""
    return ConfigReadResult(
        tenant_id=TENANT_ID,
        tier="starter",
        version=version,
        config=config or {"brand_name": "My Store", "brand_voice": "friendly"},
        from_cache=False,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_activation_service() -> AsyncMock:
    """Build a mock ActivationService with sensible defaults."""
    svc = AsyncMock()
    svc.get_draft_state = AsyncMock(return_value=_draft_state_no_changes())
    svc.has_pending_changes = AsyncMock(return_value=False)
    svc.save_draft = AsyncMock(return_value=DraftSaveResult(
        success=True,
        version=2,
        changes={"brand_name": "New Brand"},
        state="draft",
    ))
    svc.activate = AsyncMock(return_value=ActivationResult(
        success=True,
        version=2,
        activated_at=DRAFT_ACTIVATED_AT,
    ))
    svc.discard_draft = AsyncMock(return_value=True)
    svc.restore_previous = AsyncMock(return_value=RestoreResult(
        success=True,
        restored_version=1,
        restored_activated_at=ACTIVE_ACTIVATED_AT,
    ))
    svc.reinitialize_to_defaults = AsyncMock(return_value=DraftSaveResult(
        success=True,
        version=2,
        changes={"brand_name": "Default Store"},
        state="draft",
    ))
    return svc


@pytest.fixture
def mock_config_processor() -> AsyncMock:
    """Build a mock TenantConfigProcessor with sensible defaults."""
    proc = AsyncMock()
    proc.get_config = AsyncMock(return_value=_config_read_result())
    proc.validate_only = AsyncMock()
    proc.get_config_diff = AsyncMock(return_value={})
    proc.list_versions = AsyncMock(return_value=[])
    proc.get_version = AsyncMock(return_value=None)
    return proc


@pytest.fixture
def client(
    mock_activation_service: AsyncMock,
    mock_config_processor: AsyncMock,
) -> TestClient:
    """FastAPI test client with config router, mocked services, and auth override."""
    app = FastAPI()
    app.include_router(router)

    # Override the tenant context dependency to bypass auth middleware
    ctx = _make_context()
    app.dependency_overrides[get_tenant_context] = lambda: ctx

    with (
        patch(
            "src.multi_tenant.tenant_config_api.get_activation_service",
            return_value=mock_activation_service,
        ),
        patch(
            "src.multi_tenant.tenant_config_api.get_config_processor",
            return_value=mock_config_processor,
        ),
    ):
        yield TestClient(app)


@pytest.fixture
def pro_client(
    mock_activation_service: AsyncMock,
    mock_config_processor: AsyncMock,
) -> TestClient:
    """FastAPI test client authenticated as a Professional-tier tenant."""
    app = FastAPI()
    app.include_router(router)

    ctx = _make_context(tier=TenantTier.PROFESSIONAL)
    app.dependency_overrides[get_tenant_context] = lambda: ctx

    with (
        patch(
            "src.multi_tenant.tenant_config_api.get_activation_service",
            return_value=mock_activation_service,
        ),
        patch(
            "src.multi_tenant.tenant_config_api.get_config_processor",
            return_value=mock_config_processor,
        ),
    ):
        yield TestClient(app)


# ---------------------------------------------------------------------------
# 1. GET /api/config/activation-status
# ---------------------------------------------------------------------------


class TestActivationStatus:
    """Tests for GET /api/config/activation-status."""

    def test_no_pending_changes(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Returns has_pending_changes=False when no draft exists."""
        mock_activation_service.get_draft_state.return_value = _draft_state_no_changes()

        resp = client.get("/api/config/activation-status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["has_pending_changes"] is False
        assert data["active_version"] == 1
        assert data["active_activated_at"] == ACTIVE_ACTIVATED_AT
        assert data["draft_version"] is None

    def test_has_pending_changes(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Returns has_pending_changes=True with draft version when draft exists."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes()

        resp = client.get("/api/config/activation-status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["has_pending_changes"] is True
        assert data["active_version"] == 1
        assert data["draft_version"] == 2

    def test_active_version_zero_when_no_active(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Returns active_version=0 when no active config exists (fresh tenant)."""
        mock_activation_service.get_draft_state.return_value = DraftState(
            has_pending_changes=False,
            active_version=0,
            active_activated_at=None,
        )

        resp = client.get("/api/config/activation-status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["active_version"] == 0
        assert data["active_activated_at"] is None
        assert data["draft_version"] is None

    def test_passes_tenant_id_and_tier(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Endpoint passes tenant_id and resolved tier to the service."""
        mock_activation_service.get_draft_state.return_value = _draft_state_no_changes()

        client.get("/api/config/activation-status")

        mock_activation_service.get_draft_state.assert_called_once()
        call_args = mock_activation_service.get_draft_state.call_args
        assert call_args[0][0] == TENANT_ID
        assert call_args[0][1] == TenantTier.STARTER


# ---------------------------------------------------------------------------
# 2. GET /api/config/draft
# ---------------------------------------------------------------------------


class TestDraftState:
    """Tests for GET /api/config/draft."""

    def test_no_draft(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Returns has_pending_changes=False and empty fields when no draft."""
        mock_activation_service.get_draft_state.return_value = _draft_state_no_changes()

        resp = client.get("/api/config/draft")

        assert resp.status_code == 200
        data = resp.json()
        assert data["has_pending_changes"] is False
        assert data["changed_fields"] == []
        assert data["draft_config"] == {}
        assert data["active_config"] == {}

    def test_with_draft(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Returns full draft state with changed fields and configs."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes(
            changed_fields=["brand_name", "brand_voice"],
            draft_config={"brand_name": "New", "brand_voice": "professional"},
            active_config={"brand_name": "Old", "brand_voice": "friendly"},
        )

        resp = client.get("/api/config/draft")

        assert resp.status_code == 200
        data = resp.json()
        assert data["has_pending_changes"] is True
        assert data["active_version"] == 1
        assert data["draft_version"] == 2
        assert set(data["changed_fields"]) == {"brand_name", "brand_voice"}
        assert data["draft_config"]["brand_name"] == "New"
        assert data["active_config"]["brand_name"] == "Old"

    def test_draft_version_included(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """draft_version is populated when a draft exists."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes(
            draft_version=5,
        )

        resp = client.get("/api/config/draft")

        assert resp.status_code == 200
        assert resp.json()["draft_version"] == 5

    def test_active_activated_at_in_response(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """active_activated_at is present in the response."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes()

        resp = client.get("/api/config/draft")

        assert resp.status_code == 200
        assert resp.json()["active_activated_at"] == ACTIVE_ACTIVATED_AT


# ---------------------------------------------------------------------------
# 3. POST /api/config/draft/activate
# ---------------------------------------------------------------------------


class TestActivateDraft:
    """Tests for POST /api/config/draft/activate."""

    def test_success(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Successful activation returns version and activated_at."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=True,
            version=3,
            activated_at=DRAFT_ACTIVATED_AT,
            warnings=[],
        )

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["version"] == 3
        assert data["activated_at"] == DRAFT_ACTIVATED_AT
        assert data["errors"] == []

    def test_success_with_warnings(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Activation succeeds but returns warnings (e.g. no KB articles)."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=True,
            version=2,
            activated_at=DRAFT_ACTIVATED_AT,
            warnings=[{
                "field": "knowledge_base",
                "message": "No published knowledge base articles",
            }],
        )

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["warnings"]) == 1
        assert data["warnings"][0]["field"] == "knowledge_base"

    def test_validation_failure(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Activation fails with 422 when hard validation errors exist."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=False,
            errors=[{
                "field": "brand_name",
                "message": "Brand name is required before activation",
                "page": "agent-configuration",
            }],
            warnings=[],
        )

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail["success"] is False
        assert len(detail["errors"]) == 1
        assert detail["errors"][0]["field"] == "brand_name"

    def test_no_draft_to_activate(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Activation fails with 422 when no draft exists."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=False,
            errors=[{"field": "_system", "message": "Save your configuration first. Go to Agent Configuration, review your settings, and click 'Save draft inputs' before activating."}],
        )

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail["success"] is False
        assert any(
            e["message"] == "Save your configuration first. Go to Agent Configuration, review your settings, and click 'Save draft inputs' before activating." for e in detail["errors"]
        )

    def test_passes_actor_to_service(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Activation passes the derived actor to the service."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=True, version=2, activated_at=DRAFT_ACTIVATED_AT,
        )

        client.post("/api/config/draft/activate")

        mock_activation_service.activate.assert_called_once()
        call_kwargs = mock_activation_service.activate.call_args
        assert call_kwargs[1]["tenant_id"] == TENANT_ID

    def test_multiple_validation_errors(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Multiple hard errors are all returned in the 422 response."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=False,
            errors=[
                {"field": "brand_name", "message": "Brand name is required"},
                {"field": "widget_key", "message": "Widget key is missing"},
            ],
        )

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert len(detail["errors"]) == 2


# ---------------------------------------------------------------------------
# 4. POST /api/config/draft/discard
# ---------------------------------------------------------------------------


class TestDiscardDraft:
    """Tests for POST /api/config/draft/discard."""

    def test_discard_success(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Discard returns success=True and appropriate message when draft existed."""
        mock_activation_service.discard_draft.return_value = True

        resp = client.post("/api/config/draft/discard")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["message"] == "Draft discarded"

    def test_discard_no_draft(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Discard returns success=True but different message when no draft existed."""
        mock_activation_service.discard_draft.return_value = False

        resp = client.post("/api/config/draft/discard")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["message"] == "No draft to discard"

    def test_discard_passes_tenant_id(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Discard passes tenant_id to the service."""
        mock_activation_service.discard_draft.return_value = True

        client.post("/api/config/draft/discard")

        mock_activation_service.discard_draft.assert_called_once()
        call_kwargs = mock_activation_service.discard_draft.call_args
        assert call_kwargs[1]["tenant_id"] == TENANT_ID


# ---------------------------------------------------------------------------
# 5. POST /api/config/restore
# ---------------------------------------------------------------------------


class TestRestorePrevious:
    """Tests for POST /api/config/restore."""

    def test_restore_success(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Restore returns the restored version and activation timestamp."""
        mock_activation_service.restore_previous.return_value = RestoreResult(
            success=True,
            restored_version=1,
            restored_activated_at=ACTIVE_ACTIVATED_AT,
        )

        resp = client.post("/api/config/restore")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["restored_version"] == 1
        assert data["restored_activated_at"] == ACTIVE_ACTIVATED_AT

    def test_restore_no_previous(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Restore fails with 400 when no previous snapshot exists."""
        mock_activation_service.restore_previous.return_value = RestoreResult(
            success=False,
            error="No previous configuration to restore",
        )

        resp = client.post("/api/config/restore")

        assert resp.status_code == 400
        assert "No previous configuration" in resp.json()["detail"]

    def test_restore_passes_tier_and_actor(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Restore passes tenant_id, tier, and actor to the service."""
        mock_activation_service.restore_previous.return_value = RestoreResult(
            success=True, restored_version=1,
            restored_activated_at=ACTIVE_ACTIVATED_AT,
        )

        client.post("/api/config/restore")

        mock_activation_service.restore_previous.assert_called_once()
        call_kwargs = mock_activation_service.restore_previous.call_args[1]
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["tier"] == TenantTier.STARTER

    def test_restore_custom_error_message(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Restore surfaces the service error message in the 400 response."""
        mock_activation_service.restore_previous.return_value = RestoreResult(
            success=False,
            error="Service not configured",
        )

        resp = client.post("/api/config/restore")

        assert resp.status_code == 400
        assert resp.json()["detail"] == "Service not configured"

    def test_restore_null_error_uses_default(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Restore falls back to default message when error is None."""
        mock_activation_service.restore_previous.return_value = RestoreResult(
            success=False,
            error=None,
        )

        resp = client.post("/api/config/restore")

        assert resp.status_code == 400
        assert "No previous configuration to restore" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 6. PUT /api/config — saves to draft
# ---------------------------------------------------------------------------


class TestUpdateConfigDraft:
    """Tests for PUT /api/config — Save → Activate model."""

    def test_save_to_draft_success(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """PUT /api/config saves changes to draft and returns state=draft."""
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=True,
            version=2,
            changes={"brand_name": "New Brand"},
            state="draft",
        )

        resp = client.put(
            "/api/config",
            json={"fields": {"brand_name": "New Brand"}},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["version"] == 2
        assert data["state"] == "draft"
        assert data["changes"] == {"brand_name": "New Brand"}

    def test_save_empty_fields_returns_400(
        self, client: TestClient,
    ) -> None:
        """PUT /api/config with empty fields returns 400."""
        resp = client.put("/api/config", json={"fields": {}})

        assert resp.status_code == 400
        assert "No configuration fields" in resp.json()["detail"]

    def test_save_validation_error_returns_422(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """PUT /api/config returns 422 when validation fails."""
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=False,
            errors=[{"field": "brand_name", "message": "Value too long"}],
            warnings=[],
        )

        resp = client.put(
            "/api/config",
            json={"fields": {"brand_name": "x" * 500}},
        )

        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail["success"] is False
        assert len(detail["errors"]) == 1

    def test_save_with_warnings(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """PUT /api/config returns warnings alongside success."""
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=True,
            version=3,
            changes={"escalation_email": "team@example.com"},
            warnings=[{
                "field": "escalation_email",
                "message": "Escalation email should be verified",
            }],
            state="draft",
        )

        resp = client.put(
            "/api/config",
            json={"fields": {"escalation_email": "team@example.com"}},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["warnings"]) == 1

    def test_save_passes_tier_and_actor(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """PUT /api/config passes the correct tier and actor to save_draft."""
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=True, version=2, changes={"brand_name": "X"}, state="draft",
        )

        client.put(
            "/api/config",
            json={"fields": {"brand_name": "X"}},
        )

        mock_activation_service.save_draft.assert_called_once()
        call_kwargs = mock_activation_service.save_draft.call_args[1]
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["tier"] == TenantTier.STARTER
        assert call_kwargs["changes"] == {"brand_name": "X"}
        # Actor is derived from context (no user_id → tenant prefix)
        assert "tenant:" in call_kwargs["actor"]

    def test_save_multiple_fields(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """PUT /api/config saves multiple fields at once."""
        fields = {"brand_name": "Store", "brand_voice": "professional"}
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=True, version=2, changes=fields, state="draft",
        )

        resp = client.put("/api/config", json={"fields": fields})

        assert resp.status_code == 200
        assert resp.json()["changes"] == fields


# ---------------------------------------------------------------------------
# 7. GET /api/config?state=draft — returns draft config
# ---------------------------------------------------------------------------


class TestGetConfigDraftState:
    """Tests for GET /api/config?state=draft."""

    def test_get_draft_when_draft_exists(
        self,
        client: TestClient,
        mock_activation_service: AsyncMock,
    ) -> None:
        """GET /api/config?state=draft returns draft config with state=draft."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes(
            draft_version=3,
            draft_config={"brand_name": "Draft Brand", "brand_voice": "bold"},
        )

        resp = client.get("/api/config?state=draft")

        assert resp.status_code == 200
        data = resp.json()
        assert data["state"] == "draft"
        assert data["version"] == 3
        assert data["config"]["brand_name"] == "Draft Brand"

    def test_get_draft_falls_back_to_active(
        self,
        client: TestClient,
        mock_activation_service: AsyncMock,
        mock_config_processor: AsyncMock,
    ) -> None:
        """GET /api/config?state=draft returns active config when no draft."""
        mock_activation_service.get_draft_state.return_value = _draft_state_no_changes()
        mock_config_processor.get_config.return_value = _config_read_result(version=1)

        resp = client.get("/api/config?state=draft")

        assert resp.status_code == 200
        data = resp.json()
        assert data["state"] == "active"
        assert data["version"] == 1

    def test_get_active_config_default(
        self,
        client: TestClient,
        mock_config_processor: AsyncMock,
    ) -> None:
        """GET /api/config (no state param) returns active config."""
        mock_config_processor.get_config.return_value = _config_read_result(version=1)

        resp = client.get("/api/config")

        assert resp.status_code == 200
        data = resp.json()
        assert data["state"] == "active"
        assert data["tenant_id"] == TENANT_ID

    def test_get_active_config_from_cache(
        self,
        client: TestClient,
        mock_config_processor: AsyncMock,
    ) -> None:
        """GET /api/config reports from_cache when processor uses cache."""
        cached_result = ConfigReadResult(
            tenant_id=TENANT_ID,
            tier="starter",
            version=1,
            config={"brand_name": "Cached"},
            from_cache=True,
        )
        mock_config_processor.get_config.return_value = cached_result

        resp = client.get("/api/config")

        assert resp.status_code == 200
        assert resp.json()["from_cache"] is True


# ---------------------------------------------------------------------------
# 8. POST /api/config/reset — creates draft from defaults
# ---------------------------------------------------------------------------


class TestResetConfig:
    """Tests for POST /api/config/reset."""

    def test_reset_creates_draft(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """POST /api/config/reset creates a draft from tier defaults."""
        mock_activation_service.reinitialize_to_defaults.return_value = DraftSaveResult(
            success=True,
            version=2,
            changes={"brand_name": "Default Store", "brand_voice": "friendly"},
            state="draft",
        )

        resp = client.post("/api/config/reset")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["state"] == "draft"
        assert data["version"] == 2

    def test_reset_passes_tier(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """POST /api/config/reset passes the correct tier to the service."""
        mock_activation_service.reinitialize_to_defaults.return_value = DraftSaveResult(
            success=True, version=2, changes={}, state="draft",
        )

        client.post("/api/config/reset")

        mock_activation_service.reinitialize_to_defaults.assert_called_once()
        call_kwargs = mock_activation_service.reinitialize_to_defaults.call_args[1]
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["tier"] == TenantTier.STARTER

    def test_reset_professional_tier(
        self, pro_client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """POST /api/config/reset resolves Professional tier correctly."""
        mock_activation_service.reinitialize_to_defaults.return_value = DraftSaveResult(
            success=True, version=2, changes={}, state="draft",
        )

        resp = pro_client.post("/api/config/reset")

        assert resp.status_code == 200
        call_kwargs = mock_activation_service.reinitialize_to_defaults.call_args[1]
        assert call_kwargs["tier"] == TenantTier.PROFESSIONAL

    def test_reset_service_failure(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """POST /api/config/reset returns error fields when service fails."""
        mock_activation_service.reinitialize_to_defaults.return_value = DraftSaveResult(
            success=False,
            errors=[{"field": "_system", "message": "Service not configured"}],
        )

        resp = client.post("/api/config/reset")

        # Note: reset endpoint does not raise 422; it returns the result as-is
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False


# ---------------------------------------------------------------------------
# 9. POST /api/config/rollback — loads previous version as draft
# ---------------------------------------------------------------------------


class TestRollbackConfig:
    """Tests for POST /api/config/rollback."""

    def test_rollback_success(
        self,
        client: TestClient,
        mock_activation_service: AsyncMock,
        mock_config_processor: AsyncMock,
    ) -> None:
        """Rollback loads target version as draft and returns success."""
        target_config = _config_read_result(version=1, config={"brand_name": "V1"})
        mock_config_processor.get_version.return_value = target_config
        mock_config_processor.get_config.return_value = _config_read_result(version=3)
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=True, version=4, changes={"brand_name": "V1"}, state="draft",
        )

        resp = client.post("/api/config/rollback", json={"target_version": 1})

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["to_version"] == 1
        assert data["from_version"] == 3

    def test_rollback_version_not_found(
        self,
        client: TestClient,
        mock_config_processor: AsyncMock,
    ) -> None:
        """Rollback returns 404 when target version does not exist."""
        mock_config_processor.get_version.return_value = None

        resp = client.post("/api/config/rollback", json={"target_version": 99})

        assert resp.status_code == 404
        assert "version 99 not found" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 10. Auth enforcement
# ---------------------------------------------------------------------------


class TestAuthEnforcement:
    """Verify that endpoints require authentication."""

    def _make_unauthenticated_client(self) -> TestClient:
        """Build a client without any tenant context override (no auth)."""
        app = FastAPI()
        app.include_router(router)
        # Do NOT override get_tenant_context — it will raise an error
        # when FastAPI tries to resolve the dependency without middleware
        return TestClient(app, raise_server_exceptions=False)

    def test_activation_status_requires_auth(self) -> None:
        """GET /activation-status fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.get("/api/config/activation-status")
        # Without auth middleware, Depends(get_tenant_context) should fail
        assert resp.status_code in (401, 403, 422, 500)

    def test_draft_requires_auth(self) -> None:
        """GET /draft fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.get("/api/config/draft")
        assert resp.status_code in (401, 403, 422, 500)

    def test_activate_requires_auth(self) -> None:
        """POST /draft/activate fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.post("/api/config/draft/activate")
        assert resp.status_code in (401, 403, 422, 500)

    def test_discard_requires_auth(self) -> None:
        """POST /draft/discard fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.post("/api/config/draft/discard")
        assert resp.status_code in (401, 403, 422, 500)

    def test_restore_requires_auth(self) -> None:
        """POST /restore fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.post("/api/config/restore")
        assert resp.status_code in (401, 403, 422, 500)

    def test_update_requires_auth(self) -> None:
        """PUT /api/config fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.put(
            "/api/config",
            json={"fields": {"brand_name": "Test"}},
        )
        assert resp.status_code in (401, 403, 422, 500)

    def test_reset_requires_auth(self) -> None:
        """POST /api/config/reset fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.post("/api/config/reset")
        assert resp.status_code in (401, 403, 422, 500)

    def test_get_config_requires_auth(self) -> None:
        """GET /api/config fails without authentication."""
        client = self._make_unauthenticated_client()
        resp = client.get("/api/config")
        assert resp.status_code in (401, 403, 422, 500)


# ---------------------------------------------------------------------------
# 11. Response model structure
# ---------------------------------------------------------------------------


class TestResponseModelStructure:
    """Validate that API responses contain all expected fields."""

    def test_activation_status_response_fields(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """ActivationStatusResponse contains all documented fields."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes()

        resp = client.get("/api/config/activation-status")

        assert resp.status_code == 200
        data = resp.json()
        expected_keys = {
            "has_pending_changes", "active_version",
            "active_activated_at", "draft_version",
        }
        assert expected_keys <= set(data.keys())

    def test_draft_state_response_fields(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """DraftStateResponse contains all documented fields."""
        mock_activation_service.get_draft_state.return_value = _draft_state_with_changes()

        resp = client.get("/api/config/draft")

        assert resp.status_code == 200
        data = resp.json()
        expected_keys = {
            "has_pending_changes", "active_version",
            "active_activated_at", "draft_version",
            "changed_fields", "draft_config", "active_config",
        }
        assert expected_keys <= set(data.keys())

    def test_activate_response_fields(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """ActivateResponse contains all documented fields."""
        mock_activation_service.activate.return_value = ActivationResult(
            success=True, version=2, activated_at=DRAFT_ACTIVATED_AT,
        )

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 200
        data = resp.json()
        expected_keys = {
            "success", "version", "activated_at",
            "errors", "warnings",
        }
        assert expected_keys <= set(data.keys())

    def test_activate_response_survives_none_warnings(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """Activation must not 500 when ActivationResult has None warnings/errors.

        Regression: ActivateResponse Pydantic model rejects None for list fields.
        The ``or []`` coercion in the endpoint handler prevents the 500.
        """
        result = ActivationResult(
            success=True, version=3, activated_at=DRAFT_ACTIVATED_AT,
        )
        # Simulate the old bug: ``warnings=result_warnings or None`` → None
        result.warnings = None  # type: ignore[assignment]
        result.errors = None  # type: ignore[assignment]
        mock_activation_service.activate.return_value = result

        resp = client.post("/api/config/draft/activate")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["warnings"] == []
        assert data["errors"] == []

    def test_discard_response_fields(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """DiscardResponse contains all documented fields."""
        mock_activation_service.discard_draft.return_value = True

        resp = client.post("/api/config/draft/discard")

        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        assert "message" in data

    def test_restore_response_fields(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """RestoreResponse contains all documented fields."""
        mock_activation_service.restore_previous.return_value = RestoreResult(
            success=True, restored_version=1,
            restored_activated_at=ACTIVE_ACTIVATED_AT,
        )

        resp = client.post("/api/config/restore")

        assert resp.status_code == 200
        data = resp.json()
        expected_keys = {
            "success", "restored_version",
            "restored_activated_at", "error",
        }
        assert expected_keys <= set(data.keys())

    def test_config_update_response_state_field(
        self, client: TestClient, mock_activation_service: AsyncMock,
    ) -> None:
        """ConfigUpdateResponse includes state=draft on save."""
        mock_activation_service.save_draft.return_value = DraftSaveResult(
            success=True, version=2, changes={"brand_name": "X"}, state="draft",
        )

        resp = client.put("/api/config", json={"fields": {"brand_name": "X"}})

        assert resp.status_code == 200
        data = resp.json()
        expected_keys = {
            "success", "version", "errors", "warnings",
            "changes", "state",
        }
        assert expected_keys <= set(data.keys())
        assert data["state"] == "draft"
