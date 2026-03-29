"""Team-member direct agent chat tests (SPEC-1862, Phase 3).

Tests for target_agent_id routing, agent_access validation,
activation-gate bypass, and actor/channel metadata.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect

import pytest

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.events import InvocationEventBus
from src.agents.plugins.registry import PluginAgentRegistry
from src.chat.pipeline.intent_router import (
    IntentRouter,
    RouteTarget,
)


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()
    yield
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()


@pytest.fixture
def registry():
    reg = PluginAgentRegistry.get_instance()
    reg.load_from_yaml()
    return reg


@pytest.fixture
def router():
    return IntentRouter()


@pytest.fixture
def binding_svc():
    return SkillBindingService.get_instance()


# ---------------------------------------------------------------------------
# IntentRouter: target_agent_id routing
# ---------------------------------------------------------------------------


class TestTargetAgentRouting:
    """SPEC-1862: team member + target_agent_id routing."""

    def test_team_member_with_target_routes_to_peer_agent(self, registry, router, binding_svc):
        """Team member targeting a bound agent routes to PEER_AGENT."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.5,
            team_member_role="admin",
            target_agent_id="sales",
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"

    def test_team_member_without_target_routes_to_co_pilot(self, registry, router):
        """Team member without target_agent_id routes to CO_PILOT (backward compat)."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.5,
            team_member_role="admin",
        )
        assert route.target == RouteTarget.CO_PILOT

    def test_team_member_failed_peer_returns_error(self, registry, router):
        """Team member targeting unbound agent gets ERROR, not CO_PILOT fallback."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.5,
            team_member_role="admin",
            target_agent_id="sales",
        )
        assert route.target == RouteTarget.ERROR
        assert route.agent_id == "sales"
        assert route.error_reason is not None

    def test_customer_target_agent_has_no_effect(self, registry, router, binding_svc):
        """Customer with target_agent_id (no team_member_role) ignores the target."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            target_agent_id="sales",
            # No team_member_role — this is a customer
        )
        # Customer routing follows normal rules (registry routing_rules)
        assert route.target == RouteTarget.PEER_AGENT  # Via registry suggestion


# ---------------------------------------------------------------------------
# Agent access control
# ---------------------------------------------------------------------------


class TestAgentAccess:
    """SPEC-1862: per-team-member agent access validation."""

    def test_superadmin_has_implicit_wildcard(self):
        """superadmin/admin roles pass _validate_agent_access for any agent."""
        from src.chat.endpoints import _validate_agent_access
        from src.multi_tenant.auth import TenantContext, TeamMemberRole

        ctx = TenantContext(
            tenant_id="t-1",
            tier=None,
            status="active",
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.SUPERADMIN,
        )
        # Should not raise
        _validate_agent_access(ctx, "sales")
        _validate_agent_access(ctx, "any-agent")

    def test_admin_has_implicit_wildcard(self):
        """admin role passes for any agent."""
        from src.chat.endpoints import _validate_agent_access
        from src.multi_tenant.auth import TenantContext, TeamMemberRole

        ctx = TenantContext(
            tenant_id="t-1",
            tier=None,
            status="active",
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.ADMIN,
        )
        _validate_agent_access(ctx, "sales")

    def test_escalation_agent_limited_to_access_list(self):
        """escalation_agent without agent_access is denied."""
        from fastapi import HTTPException
        from src.chat.endpoints import _validate_agent_access
        from src.multi_tenant.auth import TenantContext, TeamMemberRole

        ctx = TenantContext(
            tenant_id="t-1",
            tier=None,
            status="active",
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.ESCALATION_AGENT,
            agent_access=(),  # No access
        )
        with pytest.raises(HTTPException) as exc_info:
            _validate_agent_access(ctx, "sales")
        assert exc_info.value.status_code == 403

    def test_escalation_agent_with_access_passes(self):
        """escalation_agent with agent in access list passes."""
        from src.chat.endpoints import _validate_agent_access
        from src.multi_tenant.auth import TenantContext, TeamMemberRole

        ctx = TenantContext(
            tenant_id="t-1",
            tier=None,
            status="active",
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.ESCALATION_AGENT,
            agent_access=("sales",),
        )
        _validate_agent_access(ctx, "sales")  # Should not raise

    def test_viewer_no_access_by_default(self):
        """viewer role with empty agent_access is denied."""
        from fastapi import HTTPException
        from src.chat.endpoints import _validate_agent_access
        from src.multi_tenant.auth import TenantContext, TeamMemberRole

        ctx = TenantContext(
            tenant_id="t-1",
            tier=None,
            status="active",
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.VIEWER,
            agent_access=(),
        )
        with pytest.raises(HTTPException) as exc_info:
            _validate_agent_access(ctx, "sales")
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestSchemaFields:
    """SPEC-1862: verify schema fields exist."""

    def test_conversation_document_has_actor_fields(self):
        """ConversationDocument has actor_type, channel_origin, target_agent_id."""
        from src.multi_tenant.cosmos_schema import ConversationDocument
        fields = ConversationDocument.model_fields
        assert "actor_type" in fields
        assert "channel_origin" in fields
        assert "target_agent_id" in fields
        # Check defaults
        assert fields["actor_type"].default == "customer"
        assert fields["channel_origin"].default == "widget"
        assert fields["target_agent_id"].default == ""

    def test_team_member_document_has_agent_access(self):
        """TeamMemberDocument has agent_access field."""
        from src.multi_tenant.cosmos_schema import TeamMemberDocument
        doc = TeamMemberDocument(
            id="t-1:test@example.com", tenant_id="t-1",
            email="test@example.com", display_name="Test",
            role="viewer",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        assert hasattr(doc, "agent_access")
        assert doc.agent_access == []

    def test_conversation_start_request_has_target_agent(self):
        """ConversationStartRequest accepts target_agent_id."""
        from src.chat.models import ConversationStartRequest
        req = ConversationStartRequest(target_agent_id="sales")
        assert req.target_agent_id == "sales"

    def test_conversation_state_response_has_target_agent(self):
        """ConversationStateResponse has target_agent_id field."""
        from src.chat.models import ConversationStateResponse
        assert "target_agent_id" in ConversationStateResponse.model_fields


# ---------------------------------------------------------------------------
# Integration: IntentRouter ERROR route
# ---------------------------------------------------------------------------


class TestErrorRoute:
    """SPEC-1862: ERROR route for explicit target failures."""

    def test_error_route_exists_in_enum(self):
        """RouteTarget has ERROR value."""
        assert RouteTarget.ERROR.value == "error"

    def test_orchestrator_handles_error_route(self):
        """execute() handles RouteTarget.ERROR with visible error message."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator.ChatPipeline.execute)
        assert "RouteTarget.ERROR" in source

    def test_orchestrator_accepts_target_agent_id(self):
        """execute() accepts target_agent_id parameter."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        sig = inspect.signature(ChatPipeline.execute)
        assert "target_agent_id" in sig.parameters

    def test_activation_gate_bypassed_for_team_members(self):
        """Endpoint code checks is_team_member before activation gate."""
        from src.chat import endpoints
        source = inspect.getsource(endpoints.start_conversation)
        assert "is_team_member" in source
        assert "if not is_team_member:" in source
