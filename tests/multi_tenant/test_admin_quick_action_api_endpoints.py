"""Tests for Admin Quick Action API endpoint specifications.

Covers:
    - Router prefix verification
    - list_quick_actions returns empty list when repo returns []
    - get_quick_action returns matching action from repo
    - seed_quick_actions triggers seeding when list is empty

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_quick_action_api import (
    configure_admin_quick_action_services,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", "test-tenant-001")
    ctx.tier = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = overrides.get("team_member_role", None)
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


# ---------------------------------------------------------------------------
# QA-01: Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Verify the quick action router is mounted at /api/admin/quick-actions."""

    def test_router_prefix_is_api_admin_quick_actions(self):
        assert router.prefix == "/api/admin/quick-actions"


# ---------------------------------------------------------------------------
# QA-02: list_quick_actions returns empty list
# ---------------------------------------------------------------------------


class TestListQuickActions:
    """GET /api/admin/quick-actions returns empty list from empty repo."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.prefs_repo = MagicMock()
        configure_admin_quick_action_services(self.prefs_repo)
        yield
        configure_admin_quick_action_services(None)

    @pytest.mark.asyncio
    async def test_list_empty_actions(self):
        """list_quick_actions returns empty when repo returns []."""
        from src.multi_tenant.admin_quick_action_api import list_quick_actions

        self.prefs_repo.get_quick_actions = AsyncMock(return_value=[])

        ctx = _ctx()
        response = await list_quick_actions(ctx=ctx)

        self.prefs_repo.get_quick_actions.assert_called_once_with("test-tenant-001")
        assert response.tenant_id == "test-tenant-001"
        assert response.total_count == 0
        assert response.actions == []


# ---------------------------------------------------------------------------
# QA-03: get_quick_action returns matching action
# ---------------------------------------------------------------------------


class TestGetQuickAction:
    """GET /api/admin/quick-actions/{id} returns matching action."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.prefs_repo = MagicMock()
        configure_admin_quick_action_services(self.prefs_repo)
        yield
        configure_admin_quick_action_services(None)

    @pytest.mark.asyncio
    async def test_get_existing_action(self):
        """get_quick_action returns the action when found by ID."""
        from src.multi_tenant.admin_quick_action_api import get_quick_action

        self.prefs_repo.get_quick_actions = AsyncMock(return_value=[
            {
                "id": "qa-1",
                "label": "Test",
                "prompt_template": "t",
                "is_active": True,
                "sort_order": 0,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            },
        ])

        ctx = _ctx()
        response = await get_quick_action("qa-1", ctx=ctx)

        assert response.id == "qa-1"
        assert response.label == "Test"
        assert response.prompt_template == "t"
        assert response.is_active is True


# ---------------------------------------------------------------------------
# QA-04: seed_quick_actions triggers seeding when empty
# ---------------------------------------------------------------------------


class TestSeedQuickActions:
    """POST /api/admin/quick-actions/seed creates starter actions when empty."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.prefs_repo = MagicMock()
        configure_admin_quick_action_services(self.prefs_repo)
        yield
        configure_admin_quick_action_services(None)

    @pytest.mark.asyncio
    async def test_seed_when_no_existing_actions(self):
        """seed_quick_actions creates 4 starter actions when none exist."""
        from src.multi_tenant.admin_quick_action_api import seed_quick_actions

        self.prefs_repo.list_quick_actions = AsyncMock(return_value=[])
        self.prefs_repo.upsert_quick_action = AsyncMock()

        ctx = _ctx()
        response = await seed_quick_actions(ctx=ctx)

        assert response["seeded"] == 4
        assert len(response["ids"]) == 4
        assert self.prefs_repo.upsert_quick_action.call_count == 4
