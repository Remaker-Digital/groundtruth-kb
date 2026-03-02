"""Tests for backend RBAC enforcement (WI #295 Phase 3).

Covers:
    - RBAC-01: Admin role accesses admin-only path → 200
    - RBAC-02: Superadmin role accesses admin-only path → 200
    - RBAC-03: Escalation agent accesses admin-only path → 403
    - RBAC-04: Viewer role accesses admin-only path → 403
    - RBAC-05: Escalation agent accesses inbox path → allowed (no raise)
    - RBAC-06: Viewer accesses /api/admin/team/whoami → allowed (no raise)
    - RBAC-07: Tenant-level API key (no role) accesses admin path → allowed
    - RBAC-08: is_admin_only_path correctness for all prefix categories
    - RBAC-09: enforce_rbac integration via get_tenant_context dependency

Test plan reference: §5.12 (RBAC Enforcement — WI #295 Phase 3)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TeamMemberRole
from src.multi_tenant.middleware import (
    _ADMIN_ONLY_PREFIXES,
    _ALL_ROLES_PREFIXES,
    _RBAC_OPEN_PATHS,
    enforce_rbac,
    get_tenant_context,
    is_admin_only_path,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_ctx(role: TeamMemberRole | None = None, **kwargs) -> TenantContext:
    """Create a minimal TenantContext for RBAC testing."""
    defaults = {
        "tenant_id": "t-001",
        "auth_method": "user_api_key" if role else "api_key",
        "team_member_role": role,
    }
    defaults.update(kwargs)
    return TenantContext(**defaults)


# ---------------------------------------------------------------------------
# is_admin_only_path unit tests (RBAC-08)
# ---------------------------------------------------------------------------


class TestIsAdminOnlyPath:
    """RBAC-08: Path classification correctness."""

    @pytest.mark.parametrize("path", [
        "/api/config",
        "/api/config/general",
        "/api/analytics",
        "/api/analytics/dashboard",
        "/api/audit",
        "/api/audit/log",
        "/api/gdpr",
        "/api/gdpr/erasure",
        "/api/admin/api-keys",
        "/api/admin/api-keys/rotate",
        "/api/admin/knowledge",
        "/api/admin/knowledge/sources",
        "/api/admin/integrations",
        "/api/admin/quick-actions",
        "/api/admin/profiles",
        "/api/admin/avatar",
        "/api/admin/contact",
        "/api/admin/ingestion",
        "/api/cost",
        "/api/cost/usage",
        "/api/admin/memory",
        "/api/admin/tier-upgrade",
        "/api/admin/config-lock",
        "/api/admin/team",
        "/api/admin/team/member-123",
    ])
    def test_admin_only_paths_detected(self, path):
        assert is_admin_only_path(path) is True

    @pytest.mark.parametrize("path", [
        "/api/admin/conversations",
        "/api/admin/conversations/conv-123",
        "/api/admin/conversations/conv-123/messages",
        "/api/admin/team/whoami",
        "/api/chat",
        "/api/chat/stream",
        "/api/auth/magic-link",
        "/api/auth/2fa/totp/verify",
        "/health",
        "/",
    ])
    def test_open_paths_not_classified_as_admin_only(self, path):
        assert is_admin_only_path(path) is False

    def test_whoami_overrides_team_prefix(self):
        """Whoami is explicitly open despite /api/admin/team being admin-only."""
        assert is_admin_only_path("/api/admin/team") is True
        assert is_admin_only_path("/api/admin/team/whoami") is False


# ---------------------------------------------------------------------------
# enforce_rbac unit tests (RBAC-01 to RBAC-07)
# ---------------------------------------------------------------------------


class TestEnforceRbac:
    """RBAC-01 to RBAC-07: Role-based access enforcement."""

    def test_rbac01_admin_accesses_admin_path(self):
        """Admin role can access admin-only paths without raising."""
        ctx = _make_ctx(TeamMemberRole.ADMIN)
        enforce_rbac("/api/config", ctx)  # Should not raise

    def test_rbac02_superadmin_accesses_admin_path(self):
        """Superadmin role can access admin-only paths without raising."""
        ctx = _make_ctx(TeamMemberRole.SUPERADMIN)
        enforce_rbac("/api/analytics/dashboard", ctx)  # Should not raise

    def test_rbac03_escalation_agent_blocked_on_admin_path(self):
        """Escalation agent gets 403 on admin-only paths."""
        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT)
        with pytest.raises(HTTPException) as exc_info:
            enforce_rbac("/api/config", ctx)
        assert exc_info.value.status_code == 403

    def test_rbac03b_escalation_agent_blocked_on_team_list(self):
        """Escalation agent cannot list team members."""
        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT)
        with pytest.raises(HTTPException) as exc_info:
            enforce_rbac("/api/admin/team", ctx)
        assert exc_info.value.status_code == 403

    def test_rbac04_viewer_blocked_on_admin_path(self):
        """Viewer role gets 403 on admin-only paths."""
        ctx = _make_ctx(TeamMemberRole.VIEWER)
        with pytest.raises(HTTPException) as exc_info:
            enforce_rbac("/api/admin/knowledge", ctx)
        assert exc_info.value.status_code == 403

    def test_rbac05_escalation_agent_accesses_inbox(self):
        """Escalation agent can access inbox (conversations) paths."""
        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT)
        enforce_rbac("/api/admin/conversations", ctx)  # Should not raise
        enforce_rbac("/api/admin/conversations/conv-123", ctx)  # Should not raise

    def test_rbac05b_viewer_accesses_inbox(self):
        """Viewer can access inbox paths."""
        ctx = _make_ctx(TeamMemberRole.VIEWER)
        enforce_rbac("/api/admin/conversations", ctx)  # Should not raise

    def test_rbac06_viewer_accesses_whoami(self):
        """Viewer can access /api/admin/team/whoami (role discovery)."""
        ctx = _make_ctx(TeamMemberRole.VIEWER)
        enforce_rbac("/api/admin/team/whoami", ctx)  # Should not raise

    def test_rbac06b_escalation_agent_accesses_whoami(self):
        """Escalation agent can access whoami."""
        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT)
        enforce_rbac("/api/admin/team/whoami", ctx)  # Should not raise

    def test_rbac07_tenant_api_key_no_role_passes(self):
        """Tenant-level API key (no role) treated as admin — backward compat."""
        ctx = _make_ctx(role=None)
        enforce_rbac("/api/config", ctx)  # Should not raise

    def test_rbac07b_shopify_session_no_role_passes(self):
        """Shopify session auth (no role) treated as admin."""
        ctx = _make_ctx(role=None, auth_method="shopify_session")
        enforce_rbac("/api/analytics", ctx)  # Should not raise

    @pytest.mark.parametrize("path", list(_ADMIN_ONLY_PREFIXES))
    def test_escalation_agent_blocked_on_all_admin_prefixes(self, path):
        """Escalation agent is blocked on every admin-only prefix."""
        # Skip if the path happens to also be in _RBAC_OPEN_PATHS
        if any(path.startswith(p) for p in _RBAC_OPEN_PATHS):
            return
        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT)
        with pytest.raises(HTTPException) as exc_info:
            enforce_rbac(path, ctx)
        assert exc_info.value.status_code == 403

    def test_error_message_mentions_admin(self):
        """403 error message includes 'Admin access required'."""
        ctx = _make_ctx(TeamMemberRole.VIEWER)
        with pytest.raises(HTTPException) as exc_info:
            enforce_rbac("/api/config", ctx)
        assert "Admin access required" in exc_info.value.detail


# ---------------------------------------------------------------------------
# get_tenant_context integration (RBAC-09)
# ---------------------------------------------------------------------------


class TestGetTenantContextRbac:
    """RBAC-09: enforce_rbac is wired into get_tenant_context."""

    @pytest.mark.asyncio
    async def test_viewer_on_admin_path_gets_403_from_dependency(self):
        """get_tenant_context raises 403 for viewer on admin-only path."""
        ctx = _make_ctx(TeamMemberRole.VIEWER)
        mock_request = MagicMock()
        mock_request.state.tenant_context = ctx
        mock_request.url.path = "/api/config/general"

        with pytest.raises(HTTPException) as exc_info:
            await get_tenant_context(mock_request)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_on_admin_path_returns_context(self):
        """get_tenant_context returns TenantContext for admin on admin path."""
        ctx = _make_ctx(TeamMemberRole.ADMIN)
        mock_request = MagicMock()
        mock_request.state.tenant_context = ctx
        mock_request.url.path = "/api/config/general"

        result = await get_tenant_context(mock_request)
        assert result is ctx

    @pytest.mark.asyncio
    async def test_escalation_agent_on_inbox_returns_context(self):
        """get_tenant_context returns context for agent on inbox path."""
        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT)
        mock_request = MagicMock()
        mock_request.state.tenant_context = ctx
        mock_request.url.path = "/api/admin/conversations/conv-123"

        result = await get_tenant_context(mock_request)
        assert result is ctx

    @pytest.mark.asyncio
    async def test_no_context_still_returns_401(self):
        """Missing TenantContext still returns 401 (auth before RBAC)."""
        mock_request = MagicMock()
        mock_request.state.tenant_context = None

        with pytest.raises(HTTPException) as exc_info:
            await get_tenant_context(mock_request)
        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# S130: Additional RBAC coverage (TEST-2902..2904)
# ---------------------------------------------------------------------------


class TestRbacEnforcementS130:
    """SPEC-0363 / SPEC-0426: RBAC negative and positive path coverage."""

    def test_enforce_rbac_rejects_viewer_on_admin_path(self) -> None:
        """TEST-2902: Viewer on /api/config gets 403."""
        ctx = TenantContext(
            tenant_id="t-test",
            team_member_role=TeamMemberRole.VIEWER.value,
        )
        with pytest.raises(HTTPException) as exc_info:
            enforce_rbac("/api/config", ctx)
        assert exc_info.value.status_code == 403

    def test_enforce_rbac_allows_viewer_on_inbox_path(self) -> None:
        """TEST-2903: Viewer on /api/admin/conversations does not raise."""
        ctx = TenantContext(
            tenant_id="t-test",
            team_member_role=TeamMemberRole.VIEWER.value,
        )
        # Should not raise — conversations is in _ALL_ROLES_PREFIXES
        enforce_rbac("/api/admin/conversations", ctx)

    def test_admin_only_prefixes_count(self) -> None:
        """TEST-2904: Drift detection — _ADMIN_ONLY_PREFIXES has 17 entries."""
        assert len(_ADMIN_ONLY_PREFIXES) == 17, (
            f"Expected 17 admin-only prefixes, got {len(_ADMIN_ONLY_PREFIXES)}. "
            f"If a prefix was intentionally added/removed, update SPEC-0363 and this test."
        )
