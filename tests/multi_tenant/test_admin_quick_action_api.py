"""Tests for Admin Quick Action API (WI #226-229).

Covers:
    - Quick action CRUD (create, read, update, delete)
    - Page assignment CRUD (upsert, list, delete)
    - Tier limit enforcement
    - Validation errors (invalid page_type, missing label, etc.)
    - Service injection / 503 when unconfigured
    - Config serving — GET /api/config with page_type filtering
    - Quick action resolution priority (handle > page_type > all)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    VALID_PAGE_TYPES,
    TenantStatus,
    TenantTier,
)
from src.multi_tenant.admin_quick_action_api import (
    CreateQuickActionRequest,
    QuickActionListResponse,
    QuickActionResponse,
    PageAssignmentListResponse,
    PageAssignmentResponse,
    UpsertPageAssignmentRequest,
    configure_admin_quick_action_services,
    router,
)
from src.multi_tenant.tenant_config_api import (
    QuickActionForWidget,
    _resolve_quick_actions,
    configure_quick_action_serving,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-qa-test-001"
NOW_ISO = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tenant_context(
    tenant_id: str = TENANT_ID,
    tier: TenantTier = TenantTier.STARTER,
) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=tier,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


def _make_action(
    action_id: str | None = None,
    label: str = "Test Action",
    prompt_template: str = "Tell me about {{product_title}}",
    icon: str | None = "🛒",
    is_active: bool = True,
    sort_order: int = 0,
) -> dict[str, Any]:
    return {
        "id": action_id or str(uuid.uuid4()),
        "label": label,
        "prompt_template": prompt_template,
        "icon": icon,
        "is_active": is_active,
        "sort_order": sort_order,
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
    }


def _make_assignment(
    page_type: str = "product",
    page_handle: str | None = None,
    slot_1_action_id: str | None = None,
    slot_2_action_id: str | None = None,
) -> dict[str, Any]:
    return {
        "page_type": page_type,
        "page_handle": page_handle,
        "slot_1_action_id": slot_1_action_id,
        "slot_2_action_id": slot_2_action_id,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _mock_activation_service():
    """Patch get_activation_service for all QA tests.

    The _ensure_qa_draft helper calls get_activation_service() on every
    write endpoint.  Return a mock whose ensure_draft_for_signal is a
    no-op AsyncMock so that existing tests pass without an actual
    ActivationService singleton.
    """
    mock_svc = MagicMock()
    mock_svc.ensure_draft_for_signal = AsyncMock(
        return_value=MagicMock(success=True, message="ok"),
    )
    with patch(
        "src.multi_tenant.admin_quick_action_api.get_activation_service",
        return_value=mock_svc,
    ):
        yield mock_svc


@pytest.fixture()
def mock_prefs_repo():
    """AsyncMock of PreferencesRepository with quick action methods."""
    repo = AsyncMock()
    repo._actions: list[dict[str, Any]] = []
    repo._assignments: list[dict[str, Any]] = []

    async def _get_quick_actions(tenant_id: str) -> list[dict[str, Any]]:
        return [a for a in repo._actions]

    async def _upsert_quick_action(tenant_id: str, action: dict[str, Any]) -> dict[str, Any]:
        for i, existing in enumerate(repo._actions):
            if existing.get("id") == action.get("id"):
                repo._actions[i] = action
                return action
        repo._actions.append(action)
        return action

    async def _delete_quick_action(tenant_id: str, action_id: str) -> bool:
        original_len = len(repo._actions)
        repo._actions = [a for a in repo._actions if a.get("id") != action_id]
        # Clean up assignment refs
        for asgn in repo._assignments:
            if asgn.get("slot_1_action_id") == action_id:
                asgn["slot_1_action_id"] = None
            if asgn.get("slot_2_action_id") == action_id:
                asgn["slot_2_action_id"] = None
        return len(repo._actions) < original_len

    async def _get_page_assignments(tenant_id: str) -> list[dict[str, Any]]:
        return [a for a in repo._assignments]

    async def _upsert_page_assignment(tenant_id: str, assignment: dict[str, Any]) -> dict[str, Any]:
        for i, existing in enumerate(repo._assignments):
            if (
                existing.get("page_type") == assignment.get("page_type")
                and existing.get("page_handle") == assignment.get("page_handle")
            ):
                repo._assignments[i] = assignment
                return assignment
        repo._assignments.append(assignment)
        return assignment

    async def _delete_page_assignment(
        tenant_id: str, page_type: str, page_handle: str | None = None,
    ) -> bool:
        original_len = len(repo._assignments)
        repo._assignments = [
            a for a in repo._assignments
            if not (
                a.get("page_type") == page_type
                and a.get("page_handle") == page_handle
            )
        ]
        return len(repo._assignments) < original_len

    repo.get_quick_actions = AsyncMock(side_effect=_get_quick_actions)
    repo.upsert_quick_action = AsyncMock(side_effect=_upsert_quick_action)
    repo.delete_quick_action = AsyncMock(side_effect=_delete_quick_action)
    repo.get_page_assignments = AsyncMock(side_effect=_get_page_assignments)
    repo.upsert_page_assignment = AsyncMock(side_effect=_upsert_page_assignment)
    repo.delete_page_assignment = AsyncMock(side_effect=_delete_page_assignment)
    # Active-only readers used by widget serving (_resolve_quick_actions)
    repo.get_quick_actions_active = AsyncMock(side_effect=_get_quick_actions)
    repo.get_page_assignments_active = AsyncMock(side_effect=_get_page_assignments)
    return repo


@pytest.fixture()
def qa_client(mock_prefs_repo):
    """FastAPI test client with quick action router and mocked services."""
    app = FastAPI()

    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()

    app.include_router(router)
    configure_admin_quick_action_services(prefs_repo=mock_prefs_repo)

    client = TestClient(app)
    yield client

    configure_admin_quick_action_services(prefs_repo=None)


@pytest.fixture()
def trial_client(mock_prefs_repo):
    """Client for trial-tier tenant (lowest limits)."""
    app = FastAPI()

    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context(
        tier=TenantTier.TRIAL,
    )

    app.include_router(router)
    configure_admin_quick_action_services(prefs_repo=mock_prefs_repo)

    client = TestClient(app)
    yield client

    configure_admin_quick_action_services(prefs_repo=None)


@pytest.fixture()
def unconfigured_client():
    """Client where quick action services are NOT configured — expect 503."""
    app = FastAPI()

    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()

    app.include_router(router)
    configure_admin_quick_action_services(prefs_repo=None)

    client = TestClient(app)
    yield client


# ===========================================================================
# Quick Action CRUD Tests
# ===========================================================================


class TestListQuickActions:
    """GET /api/admin/quick-actions"""

    def test_list_empty(self, qa_client):
        resp = qa_client.get("/api/admin/quick-actions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalCount"] == 0
        assert data["actions"] == []
        assert data["tenantId"] == TENANT_ID

    def test_list_with_actions(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [
            _make_action(action_id="a1", label="Action 1", sort_order=1),
            _make_action(action_id="a2", label="Action 2", sort_order=0),
        ]
        resp = qa_client.get("/api/admin/quick-actions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalCount"] == 2
        # Should be sorted by sort_order
        assert data["actions"][0]["label"] == "Action 2"
        assert data["actions"][1]["label"] == "Action 1"

    def test_list_503_when_unconfigured(self, unconfigured_client):
        resp = unconfigured_client.get("/api/admin/quick-actions")
        assert resp.status_code == 503


class TestCreateQuickAction:
    """POST /api/admin/quick-actions"""

    def test_create_success(self, qa_client):
        resp = qa_client.post("/api/admin/quick-actions", json={
            "label": "What's on sale?",
            "promptTemplate": "List current promotions for {{product_title}}",
            "icon": "🏷️",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "What's on sale?"
        assert data["promptTemplate"] == "List current promotions for {{product_title}}"
        assert data["icon"] == "🏷️"
        assert data["isActive"] is True
        assert data["sortOrder"] == 0
        assert "id" in data
        assert "createdAt" in data

    def test_create_minimal(self, qa_client):
        resp = qa_client.post("/api/admin/quick-actions", json={
            "label": "Help",
            "promptTemplate": "Help me with my order",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "Help"
        assert data["icon"] is None

    def test_create_missing_label(self, qa_client):
        resp = qa_client.post("/api/admin/quick-actions", json={
            "promptTemplate": "Some prompt",
        })
        assert resp.status_code == 422

    def test_create_missing_prompt(self, qa_client):
        resp = qa_client.post("/api/admin/quick-actions", json={
            "label": "Click me",
        })
        assert resp.status_code == 422

    def test_create_empty_label(self, qa_client):
        resp = qa_client.post("/api/admin/quick-actions", json={
            "label": "",
            "promptTemplate": "Some prompt",
        })
        assert resp.status_code == 422

    def test_create_exceeds_tier_limit(self, trial_client, mock_prefs_repo):
        # Trial allows 2 actions
        max_trial = TIER_DEFAULTS.get("trial", {}).get("max_quick_actions", 2)
        mock_prefs_repo._actions = [
            _make_action(action_id=f"existing-{i}")
            for i in range(max_trial)
        ]
        resp = trial_client.post("/api/admin/quick-actions", json={
            "label": "One more",
            "promptTemplate": "Prompt text",
        })
        assert resp.status_code == 403
        assert "limit" in resp.json()["detail"].lower()


class TestGetQuickAction:
    """GET /api/admin/quick-actions/{action_id}"""

    def test_get_existing(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [_make_action(action_id="a1", label="Test")]
        resp = qa_client.get("/api/admin/quick-actions/a1")
        assert resp.status_code == 200
        assert resp.json()["label"] == "Test"

    def test_get_not_found(self, qa_client):
        resp = qa_client.get("/api/admin/quick-actions/nonexistent")
        assert resp.status_code == 404


class TestUpdateQuickAction:
    """PUT /api/admin/quick-actions/{action_id}"""

    def test_update_label(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [_make_action(action_id="a1", label="Old")]
        resp = qa_client.put("/api/admin/quick-actions/a1", json={
            "label": "New Label",
        })
        assert resp.status_code == 200
        assert resp.json()["label"] == "New Label"

    def test_update_prompt_template(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [
            _make_action(action_id="a1", prompt_template="old prompt"),
        ]
        resp = qa_client.put("/api/admin/quick-actions/a1", json={
            "promptTemplate": "new prompt with {{page_title}}",
        })
        assert resp.status_code == 200
        assert resp.json()["promptTemplate"] == "new prompt with {{page_title}}"

    def test_update_is_active(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [_make_action(action_id="a1")]
        resp = qa_client.put("/api/admin/quick-actions/a1", json={
            "isActive": False,
        })
        assert resp.status_code == 200
        assert resp.json()["isActive"] is False

    def test_update_not_found(self, qa_client):
        resp = qa_client.put("/api/admin/quick-actions/nonexistent", json={
            "label": "Updated",
        })
        assert resp.status_code == 404

    def test_update_preserves_unchanged_fields(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [
            _make_action(action_id="a1", label="Original", icon="🎯"),
        ]
        resp = qa_client.put("/api/admin/quick-actions/a1", json={
            "label": "Changed",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "Changed"
        assert data["icon"] == "🎯"  # Preserved


class TestDeleteQuickAction:
    """DELETE /api/admin/quick-actions/{action_id}"""

    def test_delete_existing(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [_make_action(action_id="a1")]
        resp = qa_client.delete("/api/admin/quick-actions/a1")
        assert resp.status_code == 204

    def test_delete_not_found(self, qa_client):
        resp = qa_client.delete("/api/admin/quick-actions/nonexistent")
        assert resp.status_code == 404


# ===========================================================================
# Page Assignment Tests
# ===========================================================================


class TestListPageAssignments:
    """GET /api/admin/quick-actions/assignments"""

    def test_list_empty(self, qa_client):
        resp = qa_client.get("/api/admin/quick-actions/assignments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalCount"] == 0
        assert data["assignments"] == []

    def test_list_with_resolved_actions(self, qa_client, mock_prefs_repo):
        action = _make_action(action_id="a1", label="Promo")
        mock_prefs_repo._actions = [action]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="product", slot_1_action_id="a1"),
        ]
        resp = qa_client.get("/api/admin/quick-actions/assignments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalCount"] == 1
        asgn = data["assignments"][0]
        assert asgn["pageType"] == "product"
        assert asgn["slot1Action"]["label"] == "Promo"


class TestUpsertPageAssignment:
    """PUT /api/admin/quick-actions/assignments"""

    def test_create_assignment(self, qa_client, mock_prefs_repo):
        action = _make_action(action_id="a1")
        mock_prefs_repo._actions = [action]
        resp = qa_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "product",
            "slot1ActionId": "a1",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["pageType"] == "product"
        assert data["slot1ActionId"] == "a1"

    def test_update_existing_assignment(self, qa_client, mock_prefs_repo):
        action1 = _make_action(action_id="a1", label="Action 1")
        action2 = _make_action(action_id="a2", label="Action 2")
        mock_prefs_repo._actions = [action1, action2]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="home", slot_1_action_id="a1"),
        ]
        resp = qa_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "home",
            "slot1ActionId": "a1",
            "slot2ActionId": "a2",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["slot1ActionId"] == "a1"
        assert data["slot2ActionId"] == "a2"

    def test_invalid_page_type(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = [_make_action(action_id="a1")]
        resp = qa_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "invalid_page",
            "slot1ActionId": "a1",
        })
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()

    def test_nonexistent_action_id(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._actions = []
        resp = qa_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "product",
            "slot1ActionId": "nonexistent",
        })
        assert resp.status_code == 404

    def test_assignment_with_handle(self, qa_client, mock_prefs_repo):
        action = _make_action(action_id="a1")
        mock_prefs_repo._actions = [action]
        resp = qa_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "product",
            "pageHandle": "organic-cotton-tee",
            "slot1ActionId": "a1",
        })
        assert resp.status_code == 200
        assert resp.json()["pageHandle"] == "organic-cotton-tee"

    def test_assignment_tier_limit(self, trial_client, mock_prefs_repo):
        max_assignments = TIER_DEFAULTS.get("trial", {}).get(
            "max_quick_action_assignments", 2,
        )
        action = _make_action(action_id="a1")
        mock_prefs_repo._actions = [action]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type=f"type-{i}", slot_1_action_id="a1")
            for i in range(max_assignments)
        ]
        resp = trial_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "collection",
            "slot1ActionId": "a1",
        })
        assert resp.status_code == 403


class TestDeletePageAssignment:
    """DELETE /api/admin/quick-actions/assignments/{page_type}"""

    def test_delete_existing(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="product"),
        ]
        resp = qa_client.delete("/api/admin/quick-actions/assignments/product")
        assert resp.status_code == 204

    def test_delete_not_found(self, qa_client):
        resp = qa_client.delete("/api/admin/quick-actions/assignments/nonexistent")
        assert resp.status_code == 404

    def test_delete_with_handle(self, qa_client, mock_prefs_repo):
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="product", page_handle="blue-shirt"),
        ]
        resp = qa_client.delete(
            "/api/admin/quick-actions/assignments/product?page_handle=blue-shirt",
        )
        assert resp.status_code == 204


# ===========================================================================
# Route Shadowing Protection
# ===========================================================================


class TestRouteShadowing:
    """Verify that /assignments routes are NOT shadowed by /{action_id}."""

    def test_assignments_get_not_shadowed(self, qa_client):
        """GET /assignments should return 200, not try to find action with id='assignments'."""
        resp = qa_client.get("/api/admin/quick-actions/assignments")
        assert resp.status_code == 200

    def test_assignments_put_not_shadowed(self, qa_client, mock_prefs_repo):
        """PUT /assignments should return 400 (validation), not 404 (action not found)."""
        # Invalid page_type should trigger 400, NOT "Quick action not found" 404
        resp = qa_client.put("/api/admin/quick-actions/assignments", json={
            "pageType": "INVALID",
        })
        assert resp.status_code == 400


# ===========================================================================
# Config Serving — Quick Action Resolution Tests
# ===========================================================================


class TestQuickActionResolution:
    """Test _resolve_quick_actions in tenant_config_api.py."""

    @pytest.fixture(autouse=True)
    def _setup_serving(self, mock_prefs_repo):
        configure_quick_action_serving(prefs_repo=mock_prefs_repo)
        yield
        configure_quick_action_serving(prefs_repo=None)

    @pytest.mark.asyncio
    async def test_exact_handle_match(self, mock_prefs_repo):
        """Specific handle assignment takes priority over page-type-level."""
        action = _make_action(action_id="a1", label="Specific")
        generic = _make_action(action_id="a2", label="Generic")
        mock_prefs_repo._actions = [action, generic]
        mock_prefs_repo._assignments = [
            _make_assignment(
                page_type="product", page_handle="blue-shirt",
                slot_1_action_id="a1",
            ),
            _make_assignment(
                page_type="product",
                slot_1_action_id="a2",
            ),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID, {}, "product", "blue-shirt",
        )
        assert len(result) == 1
        assert result[0].label == "Specific"

    @pytest.mark.asyncio
    async def test_page_type_fallback(self, mock_prefs_repo):
        """Falls back to page-type-level when no handle match."""
        action = _make_action(action_id="a1", label="Product Default")
        mock_prefs_repo._actions = [action]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="product", slot_1_action_id="a1"),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID, {}, "product", "unknown-handle",
        )
        assert len(result) == 1
        assert result[0].label == "Product Default"

    @pytest.mark.asyncio
    async def test_all_fallback(self, mock_prefs_repo):
        """Falls back to 'all' page type when no specific match."""
        action = _make_action(action_id="a1", label="Global Fallback")
        mock_prefs_repo._actions = [action]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="all", slot_1_action_id="a1"),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID, {}, "blog", None,
        )
        assert len(result) == 1
        assert result[0].label == "Global Fallback"

    @pytest.mark.asyncio
    async def test_no_match_returns_empty(self, mock_prefs_repo):
        """Returns empty when no assignment matches."""
        mock_prefs_repo._actions = [_make_action(action_id="a1")]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="product", slot_1_action_id="a1"),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID, {}, "cart", None,
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_inactive_actions_excluded(self, mock_prefs_repo):
        """Inactive actions are not returned."""
        inactive = _make_action(action_id="a1", label="Inactive", is_active=False)
        active = _make_action(action_id="a2", label="Active", is_active=True)
        mock_prefs_repo._actions = [inactive, active]
        mock_prefs_repo._assignments = [
            _make_assignment(
                page_type="home",
                slot_1_action_id="a1",
                slot_2_action_id="a2",
            ),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID, {}, "home", None,
        )
        # Only active action returned
        assert len(result) == 1
        assert result[0].label == "Active"

    @pytest.mark.asyncio
    async def test_two_slots_returned(self, mock_prefs_repo):
        """Both slot_1 and slot_2 actions are returned."""
        a1 = _make_action(action_id="a1", label="Slot 1")
        a2 = _make_action(action_id="a2", label="Slot 2")
        mock_prefs_repo._actions = [a1, a2]
        mock_prefs_repo._assignments = [
            _make_assignment(
                page_type="collection",
                slot_1_action_id="a1",
                slot_2_action_id="a2",
            ),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID, {}, "collection", None,
        )
        assert len(result) == 2
        assert result[0].label == "Slot 1"
        assert result[1].label == "Slot 2"

    @pytest.mark.asyncio
    async def test_disabled_via_config(self, mock_prefs_repo):
        """Returns empty when widget_quick_actions_enabled is False."""
        mock_prefs_repo._actions = [_make_action(action_id="a1")]
        mock_prefs_repo._assignments = [
            _make_assignment(page_type="all", slot_1_action_id="a1"),
        ]

        result = await _resolve_quick_actions(
            TENANT_ID,
            {"widget_quick_actions_enabled": False},
            "home",
            None,
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_no_actions_returns_empty(self, mock_prefs_repo):
        """Returns empty when tenant has no quick actions."""
        result = await _resolve_quick_actions(
            TENANT_ID, {}, "home", None,
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_no_repo_returns_empty(self):
        """Returns empty when serving is not configured."""
        configure_quick_action_serving(prefs_repo=None)
        result = await _resolve_quick_actions(
            TENANT_ID, {}, "home", None,
        )
        assert result == []


# ===========================================================================
# Schema / Model Validation Tests
# ===========================================================================


class TestModels:
    """Test Pydantic model validation."""

    def test_valid_page_types(self):
        expected = {"home", "product", "collection", "cart", "search", "blog", "page", "all", "other"}
        assert VALID_PAGE_TYPES == expected

    def test_quick_action_response_camel_case(self):
        resp = QuickActionResponse(
            id="test",
            label="Test",
            prompt_template="prompt",
            is_active=True,
            sort_order=0,
            created_at=NOW_ISO,
            updated_at=NOW_ISO,
        )
        data = resp.model_dump(by_alias=True)
        assert "promptTemplate" in data
        assert "isActive" in data
        assert "sortOrder" in data
        assert "createdAt" in data

    def test_page_assignment_response_camel_case(self):
        resp = PageAssignmentResponse(
            page_type="product",
            page_handle="blue-shirt",
            slot_1_action_id="a1",
        )
        data = resp.model_dump(by_alias=True)
        assert "pageType" in data
        assert "pageHandle" in data
        assert "slot1ActionId" in data

    def test_quick_action_for_widget_shape(self):
        """Widget-facing model has minimal fields."""
        action = QuickActionForWidget(
            id="a1",
            label="Sale items",
            prompt_template="Show me {{product_title}} discounts",
            icon="🏷️",
        )
        assert action.id == "a1"
        assert action.label == "Sale items"
        assert action.icon == "🏷️"


# ===========================================================================
# Tier Limits in TIER_DEFAULTS
# ===========================================================================


class TestTierDefaults:
    """Verify quick action tier limits exist in TIER_DEFAULTS."""

    def test_trial_limits(self):
        assert "max_quick_actions" in TIER_DEFAULTS["trial"]
        assert "max_quick_action_assignments" in TIER_DEFAULTS["trial"]
        assert TIER_DEFAULTS["trial"]["max_quick_actions"] == 2
        assert TIER_DEFAULTS["trial"]["max_quick_action_assignments"] == 2

    def test_starter_limits(self):
        assert TIER_DEFAULTS["starter"]["max_quick_actions"] == 5
        assert TIER_DEFAULTS["starter"]["max_quick_action_assignments"] == 10

    def test_professional_limits(self):
        assert TIER_DEFAULTS["professional"]["max_quick_actions"] == 20
        assert TIER_DEFAULTS["professional"]["max_quick_action_assignments"] == 50

    def test_enterprise_limits(self):
        assert TIER_DEFAULTS["enterprise"]["max_quick_actions"] == 50
        assert TIER_DEFAULTS["enterprise"]["max_quick_action_assignments"] == 200

    def test_limits_increase_with_tier(self):
        tiers = ["trial", "starter", "professional", "enterprise"]
        for i in range(len(tiers) - 1):
            assert (
                TIER_DEFAULTS[tiers[i]]["max_quick_actions"]
                < TIER_DEFAULTS[tiers[i + 1]]["max_quick_actions"]
            )


# ===========================================================================
# Config Schema Field Definition
# ===========================================================================


class TestConfigSchemaField:
    """Verify widget_quick_actions_enabled field in config schema."""

    def test_field_exists_in_schema(self):
        from src.multi_tenant.tenant_config_schema import get_field_registry

        registry = get_field_registry()
        assert "widget_quick_actions_enabled" in registry

    def test_field_defaults_to_true(self):
        from src.multi_tenant.tenant_config_schema import get_field_registry

        registry = get_field_registry()
        field = registry["widget_quick_actions_enabled"]
        assert field.platform_default is True

    def test_field_is_boolean_type(self):
        from src.multi_tenant.tenant_config_schema import (
            ConfigFieldType,
            get_field_registry,
        )

        registry = get_field_registry()
        field = registry["widget_quick_actions_enabled"]
        assert field.field_type == ConfigFieldType.BOOLEAN

    def test_field_in_widget_appearance_step(self):
        from src.multi_tenant.tenant_config_schema import (
            OnboardingStep,
            get_field_registry,
        )

        registry = get_field_registry()
        field = registry["widget_quick_actions_enabled"]
        assert field.onboarding_step == OnboardingStep.WIDGET_APPEARANCE


# ===========================================================================
# Draft Signal Tests (D20 + D68)
# ===========================================================================


class TestQADraftSignal:
    """Verify that QA write endpoints call ensure_draft_for_signal (D20+D68)."""

    def test_create_quick_action_ensures_draft(
        self, qa_client, _mock_activation_service,
    ):
        """Creating a quick action triggers the qa_modified_at signal."""
        resp = qa_client.post(
            "/api/admin/quick-actions",
            json={"label": "Test", "promptTemplate": "hello"},
        )
        assert resp.status_code == 201
        _mock_activation_service.ensure_draft_for_signal.assert_called()
        call_kwargs = _mock_activation_service.ensure_draft_for_signal.call_args
        assert call_kwargs.kwargs.get("signal_field") == "qa_modified_at"

    def test_update_quick_action_ensures_draft(
        self, qa_client, mock_prefs_repo, _mock_activation_service,
    ):
        """Updating a quick action triggers the qa_modified_at signal."""
        action = _make_action(action_id="act-1")
        mock_prefs_repo._actions.append(action)

        resp = qa_client.put(
            "/api/admin/quick-actions/act-1",
            json={"label": "Updated"},
        )
        assert resp.status_code == 200
        _mock_activation_service.ensure_draft_for_signal.assert_called()
        call_kwargs = _mock_activation_service.ensure_draft_for_signal.call_args
        assert call_kwargs.kwargs.get("signal_field") == "qa_modified_at"

    def test_delete_quick_action_ensures_draft(
        self, qa_client, mock_prefs_repo, _mock_activation_service,
    ):
        """Deleting a quick action triggers the qa_modified_at signal."""
        action = _make_action(action_id="act-2")
        mock_prefs_repo._actions.append(action)

        resp = qa_client.delete("/api/admin/quick-actions/act-2")
        assert resp.status_code == 204
        _mock_activation_service.ensure_draft_for_signal.assert_called()

    def test_upsert_page_assignment_ensures_draft(
        self, qa_client, mock_prefs_repo, _mock_activation_service,
    ):
        """Upserting a page assignment triggers the qa_modified_at signal."""
        action = _make_action(action_id="act-3")
        mock_prefs_repo._actions.append(action)

        resp = qa_client.put(
            "/api/admin/quick-actions/assignments",
            json={"pageType": "product", "slot1ActionId": "act-3"},
        )
        assert resp.status_code == 200
        _mock_activation_service.ensure_draft_for_signal.assert_called()
        call_kwargs = _mock_activation_service.ensure_draft_for_signal.call_args
        assert call_kwargs.kwargs.get("signal_field") == "qa_modified_at"

    def test_delete_page_assignment_ensures_draft(
        self, qa_client, mock_prefs_repo, _mock_activation_service,
    ):
        """Deleting a page assignment triggers the qa_modified_at signal."""
        mock_prefs_repo._assignments.append(
            _make_assignment(page_type="product"),
        )

        resp = qa_client.delete(
            "/api/admin/quick-actions/assignments/product",
        )
        assert resp.status_code == 204
        _mock_activation_service.ensure_draft_for_signal.assert_called()
