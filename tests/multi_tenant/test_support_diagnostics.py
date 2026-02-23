"""Tests for HV-1 Support Diagnostics API (SD-01 to SD-18).

Covers:
    - Diagnostic snapshot returns complete data (SD-01 to SD-04)
    - Diagnostic snapshot handles missing tenant (SD-05)
    - Graceful degradation when subsystems fail (SD-06 to SD-10)
    - Errors endpoint returns entries (SD-11 to SD-13)
    - Errors endpoint handles empty results (SD-14)
    - Auth enforcement — superadmin role required (SD-15 to SD-18)

Test plan reference: HV-1 (Support Diagnostics)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.support_diagnostics import (
    TenantDiagnosticSnapshot,
    TenantErrorsResponse,
    get_tenant_diagnostic,
    get_tenant_errors,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_tenant_doc():
    """Sample tenant document for diagnostics."""
    return {
        "id": "tenant-diag-001",
        "tenant_id": "tenant-diag-001",
        "status": "active",
        "tier": "professional",
        "billing_channel": "stripe",
        "created_at": "2026-01-15T10:00:00+00:00",
        "shopify_shop_domain": "test-store.myshopify.com",
        "stripe_customer_id": "cus_test123",
        "nats_enabled": True,
    }


@pytest.fixture()
def mock_tenant_repo(sample_tenant_doc):
    """Mock TenantRepository that returns a valid tenant."""
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=sample_tenant_doc)
    return repo


@pytest.fixture()
def mock_tenant_repo_missing():
    """Mock TenantRepository that raises for missing tenant."""
    repo = AsyncMock()
    repo.read = AsyncMock(side_effect=Exception("Document not found"))
    return repo


@pytest.fixture()
def mock_prefs_repo():
    """Mock PreferencesRepository with active and draft configs."""
    repo = AsyncMock()
    repo.get_active = AsyncMock(return_value={
        "version": 3,
        "activated_at": "2026-02-01T12:00:00+00:00",
        "brand_name": "Test Brand",
        "brand_voice": "Professional and helpful",
        "model": "gpt-4o",
        "widget_key": "pk_live_abc123",
        "allowed_origins": ["https://example.com"],
    })
    repo.get_draft = AsyncMock(return_value={
        "version": 4,
        "brand_name": "Test Brand Updated",
    })
    return repo


@pytest.fixture()
def mock_kb_repo():
    """Mock KnowledgeBaseRepository returning article list."""
    repo = AsyncMock()
    repo.query = AsyncMock(return_value=[
        {"id": "kb-1", "is_active": True},
        {"id": "kb-2", "is_active": True},
        {"id": "kb-3", "is_active": False},
        {"id": "kb-4", "is_active": True},
        {"id": "kb-5", "is_active": False},
    ])
    return repo


@pytest.fixture()
def mock_team_repo():
    """Mock TeamMemberRepository returning team members."""
    repo = AsyncMock()
    repo.list_members = AsyncMock(return_value=[
        {"id": "m1", "role": "superadmin"},
        {"id": "m2", "role": "admin"},
        {"id": "m3", "role": "admin"},
        {"id": "m4", "role": "viewer"},
    ])
    return repo


@pytest.fixture()
def mock_conv_repo():
    """Mock ConversationRepository with counts and status data."""
    repo = AsyncMock()
    repo.query_count = AsyncMock(side_effect=[5, 32])  # 24h, then 7d
    repo.query = AsyncMock(side_effect=[
        # Status breakdown query
        [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"},
            {"status": "active"},
            {"status": "escalated"},
        ],
        # Last activity query (most recent conversation)
        [{"started_at": "2026-02-18T09:30:00+00:00"}],
    ])
    return repo


@pytest.fixture()
def mock_audit_repo():
    """Mock AuditLogRepository for errors endpoint."""
    repo = AsyncMock()
    container = AsyncMock()

    async def _mock_query_items(**kwargs):
        items = [
            {
                "event_type": "pipeline.error",
                "timestamp": "2026-02-18T08:00:00+00:00",
                "actor": "system",
                "payload": {"message": "LLM timeout"},
                "conversation_id": "conv-001",
            },
            {
                "event_type": "webhook.failure",
                "timestamp": "2026-02-18T07:30:00+00:00",
                "actor": "webhook",
                "payload": {"status_code": 500},
                "conversation_id": None,
            },
        ]
        for item in items:
            yield item

    container.query_items = _mock_query_items
    repo._container = container
    return repo


@pytest.fixture()
def mock_audit_repo_empty():
    """Mock AuditLogRepository that returns no errors."""
    repo = AsyncMock()
    container = AsyncMock()

    async def _mock_query_items(**kwargs):
        return
        yield  # noqa: unreachable — makes this an async generator

    container.query_items = _mock_query_items
    repo._container = container
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Mock TenantContext for superadmin access."""
    ctx = MagicMock()
    ctx.tenant_id = "provider-001"
    ctx.team_member_role = "superadmin"
    return ctx


# ---------------------------------------------------------------------------
# SD-01 to SD-04: Diagnostic snapshot returns complete data
# ---------------------------------------------------------------------------


class TestDiagnosticSnapshot:
    """SD-01 to SD-04: Comprehensive diagnostic snapshot."""

    @pytest.mark.asyncio
    async def test_sd01_snapshot_returns_basic_tenant_info(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_kb_repo, mock_team_repo, mock_conv_repo,
    ):
        """SD-01: Snapshot includes tenant basic info fields."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert isinstance(result, TenantDiagnosticSnapshot)
        assert result.tenant_id == "tenant-diag-001"
        assert result.status == "active"
        assert result.tier == "professional"
        assert result.billing_channel == "stripe"
        assert result.created_at == "2026-01-15T10:00:00+00:00"
        assert result.generated_at != ""

    @pytest.mark.asyncio
    async def test_sd02_snapshot_returns_config_state(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_kb_repo, mock_team_repo, mock_conv_repo,
    ):
        """SD-02: Snapshot includes configuration state and AI config."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert result.config_state.is_active is True
        assert result.config_state.is_configured is True
        assert result.config_state.has_pending_changes is True
        assert result.config_state.active_version == 3
        assert result.config_state.activated_at == "2026-02-01T12:00:00+00:00"
        assert result.ai_config.model == "gpt-4o"
        assert result.ai_config.brand_name_present is True
        assert result.ai_config.brand_voice_present is True

    @pytest.mark.asyncio
    async def test_sd03_snapshot_returns_kb_and_team_stats(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_kb_repo, mock_team_repo, mock_conv_repo,
    ):
        """SD-03: Snapshot includes KB stats and team breakdown."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        # KB stats
        assert result.knowledge_base.total_articles == 5
        assert result.knowledge_base.active_count == 3
        assert result.knowledge_base.draft_count == 2

        # Team info
        assert result.team.member_count == 4
        assert result.team.roles_breakdown["superadmin"] == 1
        assert result.team.roles_breakdown["admin"] == 2
        assert result.team.roles_breakdown["viewer"] == 1

    @pytest.mark.asyncio
    async def test_sd04_snapshot_returns_conversations_and_integrations(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_kb_repo, mock_team_repo, mock_conv_repo,
    ):
        """SD-04: Snapshot includes conversation stats and integration health."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
            # Explicitly set NATS as not deployed for this test
            patch("src.multi_tenant.superadmin_api._nats_mgr", None),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        # Conversation stats
        assert result.conversations.last_24h_count == 5
        assert result.conversations.last_7d_count == 32
        assert result.conversations.status_breakdown["completed"] == 3
        assert result.conversations.status_breakdown["active"] == 1
        assert result.conversations.status_breakdown["escalated"] == 1

        # Integration health
        assert result.integrations.shopify_connected is True
        assert result.integrations.stripe_connected is True
        # NATS not deployed — module-level _nats_mgr is None
        assert result.integrations.nats_deployed is False
        assert result.integrations.nats_connected is False

        # Widget
        assert result.widget.widget_key_present is True
        assert result.widget.origin_configured is True

        # Last activity
        assert result.last_activity_at == "2026-02-18T09:30:00+00:00"


# ---------------------------------------------------------------------------
# SD-05: Missing tenant
# ---------------------------------------------------------------------------


class TestDiagnosticMissingTenant:
    """SD-05: Diagnostic snapshot returns 404 for missing tenant."""

    @pytest.mark.asyncio
    async def test_sd05_missing_tenant_returns_404(
        self, superadmin_ctx, mock_tenant_repo_missing,
    ):
        """SD-05: Unknown tenant_id returns HTTP 404."""
        with patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_tenant_repo_missing,
        ):
            with pytest.raises(Exception) as exc_info:
                await get_tenant_diagnostic(
                    tenant_id="nonexistent-tenant", _ctx=superadmin_ctx,
                )
            assert exc_info.value.status_code == 404
            assert "Tenant not found" in str(exc_info.value.detail)


# ---------------------------------------------------------------------------
# SD-06 to SD-10: Graceful degradation
# ---------------------------------------------------------------------------


class TestGracefulDegradation:
    """SD-06 to SD-10: Subsystem failures produce partial data with errors."""

    @pytest.mark.asyncio
    async def test_sd06_config_failure_returns_partial(
        self, superadmin_ctx, mock_tenant_repo, mock_kb_repo,
        mock_team_repo, mock_conv_repo,
    ):
        """SD-06: Config subsystem failure still returns other data."""
        broken_prefs = AsyncMock()
        broken_prefs.get_active = AsyncMock(side_effect=RuntimeError("Cosmos timeout"))

        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=broken_prefs),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        # Should still return basic info
        assert result.tenant_id == "tenant-diag-001"
        assert result.status == "active"
        # Config should be default (failure)
        assert result.config_state.is_active is False
        # But other subsystems should still work
        assert result.knowledge_base.total_articles == 5
        assert result.team.member_count == 4
        # Error should be recorded
        assert any("config_state" in e for e in result.collection_errors)

    @pytest.mark.asyncio
    async def test_sd07_kb_failure_returns_partial(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_team_repo, mock_conv_repo,
    ):
        """SD-07: KB subsystem failure still returns other data."""
        broken_kb = AsyncMock()
        broken_kb.query = AsyncMock(side_effect=RuntimeError("Connection refused"))

        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=broken_kb),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert result.knowledge_base.total_articles == 0  # default
        assert result.config_state.is_active is True  # other subsystems ok
        assert any("knowledge_base" in e for e in result.collection_errors)

    @pytest.mark.asyncio
    async def test_sd08_team_failure_returns_partial(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_kb_repo, mock_conv_repo,
    ):
        """SD-08: Team subsystem failure still returns other data."""
        broken_team = AsyncMock()
        broken_team.list_members = AsyncMock(side_effect=RuntimeError("DB unavailable"))

        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=broken_team),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=mock_conv_repo),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert result.team.member_count == 0  # default
        assert result.knowledge_base.total_articles == 5  # other subsystems ok
        assert any("team" in e for e in result.collection_errors)

    @pytest.mark.asyncio
    async def test_sd09_conversation_failure_returns_partial(
        self, superadmin_ctx, mock_tenant_repo, mock_prefs_repo,
        mock_kb_repo, mock_team_repo,
    ):
        """SD-09: Conversation subsystem failure still returns other data."""
        broken_conv = AsyncMock()
        broken_conv.query_count = AsyncMock(side_effect=RuntimeError("Timeout"))

        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=mock_prefs_repo),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=mock_kb_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=broken_conv),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert result.conversations.last_24h_count == 0
        assert result.conversations.last_7d_count == 0
        assert result.team.member_count == 4  # other subsystems ok
        assert any("conversations" in e for e in result.collection_errors)

    @pytest.mark.asyncio
    async def test_sd10_multiple_failures_accumulate_errors(
        self, superadmin_ctx, mock_tenant_repo,
    ):
        """SD-10: Multiple subsystem failures all reported in collection_errors."""
        broken = AsyncMock()
        broken.get_active = AsyncMock(side_effect=RuntimeError("fail1"))
        broken.get_draft = AsyncMock(side_effect=RuntimeError("fail1"))
        broken_kb = AsyncMock()
        broken_kb.query = AsyncMock(side_effect=RuntimeError("fail2"))
        broken_team = AsyncMock()
        broken_team.list_members = AsyncMock(side_effect=RuntimeError("fail3"))
        broken_conv = AsyncMock()
        broken_conv.query_count = AsyncMock(side_effect=RuntimeError("fail4"))

        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.PreferencesRepository", return_value=broken),
            patch("src.multi_tenant.repositories.KnowledgeBaseRepository", return_value=broken_kb),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=broken_team),
            patch("src.multi_tenant.repositories.ConversationRepository", return_value=broken_conv),
        ):
            result = await get_tenant_diagnostic(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        # Basic info still present
        assert result.tenant_id == "tenant-diag-001"
        assert result.status == "active"
        # Multiple errors collected
        assert len(result.collection_errors) >= 4
        error_keys = " ".join(result.collection_errors)
        assert "config_state" in error_keys
        assert "knowledge_base" in error_keys
        assert "team" in error_keys
        assert "conversations" in error_keys


# ---------------------------------------------------------------------------
# SD-11 to SD-14: Errors endpoint
# ---------------------------------------------------------------------------


class TestErrorsEndpoint:
    """SD-11 to SD-14: Recent errors for a tenant."""

    @pytest.mark.asyncio
    async def test_sd11_errors_returns_entries(
        self, superadmin_ctx, mock_tenant_repo, mock_audit_repo,
    ):
        """SD-11: Errors endpoint returns error entries."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.AuditLogRepository", return_value=mock_audit_repo),
        ):
            result = await get_tenant_errors(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert isinstance(result, TenantErrorsResponse)
        assert result.tenant_id == "tenant-diag-001"
        assert result.total == 2
        assert len(result.entries) == 2
        assert result.entries[0].event_type == "pipeline.error"
        assert result.entries[0].conversation_id == "conv-001"
        assert result.entries[1].event_type == "webhook.failure"
        assert result.generated_at != ""

    @pytest.mark.asyncio
    async def test_sd12_errors_entry_fields(
        self, superadmin_ctx, mock_tenant_repo, mock_audit_repo,
    ):
        """SD-12: Each error entry has expected fields."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.AuditLogRepository", return_value=mock_audit_repo),
        ):
            result = await get_tenant_errors(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        entry = result.entries[0]
        assert entry.event_type == "pipeline.error"
        assert entry.timestamp == "2026-02-18T08:00:00+00:00"
        assert entry.actor == "system"
        assert "message" in entry.payload
        assert entry.conversation_id == "conv-001"

    @pytest.mark.asyncio
    async def test_sd13_errors_missing_tenant_returns_404(
        self, superadmin_ctx, mock_tenant_repo_missing,
    ):
        """SD-13: Errors endpoint returns 404 for unknown tenant."""
        with patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_tenant_repo_missing,
        ):
            with pytest.raises(Exception) as exc_info:
                await get_tenant_errors(
                    tenant_id="nonexistent", _ctx=superadmin_ctx,
                )
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_sd14_errors_empty_returns_zero(
        self, superadmin_ctx, mock_tenant_repo, mock_audit_repo_empty,
    ):
        """SD-14: Errors endpoint returns empty list when no errors exist."""
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.AuditLogRepository", return_value=mock_audit_repo_empty),
        ):
            result = await get_tenant_errors(
                tenant_id="tenant-diag-001", _ctx=superadmin_ctx,
            )

        assert result.total == 0
        assert result.entries == []


# ---------------------------------------------------------------------------
# SD-15 to SD-18: Auth enforcement
# ---------------------------------------------------------------------------


class TestAuthEnforcement:
    """SD-15 to SD-18: Superadmin role requirement."""

    def test_sd15_diagnostic_route_has_superadmin_dependency(self):
        """SD-15: Diagnostic endpoint has require_role(SUPERADMIN) dependency."""
        from src.multi_tenant.support_diagnostics import router

        routes = {r.path: r for r in router.routes}
        diag_route = routes.get("/api/superadmin/diagnostics/{tenant_id}")
        assert diag_route is not None
        # The router-level dependency (require_role) is applied at router creation
        assert len(router.dependencies) > 0

    def test_sd16_errors_route_has_superadmin_dependency(self):
        """SD-16: Errors endpoint has require_role(SUPERADMIN) dependency."""
        from src.multi_tenant.support_diagnostics import router

        routes = {r.path: r for r in router.routes}
        errors_route = routes.get("/api/superadmin/diagnostics/{tenant_id}/errors")
        assert errors_route is not None
        # The router-level dependency (require_role) is applied at router creation
        assert len(router.dependencies) > 0

    def test_sd17_router_has_correct_prefix(self):
        """SD-17: Router uses /api/superadmin/diagnostics prefix."""
        from src.multi_tenant.support_diagnostics import router

        assert router.prefix == "/api/superadmin/diagnostics"

    def test_sd18_router_has_correct_tags(self):
        """SD-18: Router uses Support Diagnostics tag."""
        from src.multi_tenant.support_diagnostics import router

        assert "Support Diagnostics" in router.tags
