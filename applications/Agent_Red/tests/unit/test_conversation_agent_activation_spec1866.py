# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1866 conversation-level agent activation coverage."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.events import InvocationEventBus
from src.agents.plugins.registry import PluginAgentRegistry
from src.chat.pipeline.intent_router import IntentRouter, RouteTarget
from src.multi_tenant.cosmos_schema import ConversationDocument


def _conversation_doc(**overrides):
    doc = {
        "id": "conv-1866",
        "conversation_id": "conv-1866",
        "tenant_id": "tenant-1866",
        "status": "active",
        "customer_id": "customer-1866",
        "last_activity_at": "2026-06-24T00:00:00+00:00",
        "messages": [],
        "internal_notes": [],
    }
    doc.update(overrides)
    return doc


@pytest.fixture(autouse=True)
def reset_agent_singletons():
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()
    yield
    PluginAgentRegistry.reset()
    SkillBindingService.reset()
    InvocationEventBus.reset()


@pytest.fixture
def tenant_ctx():
    return SimpleNamespace(
        tenant_id="tenant-1866",
        tier=SimpleNamespace(value="professional"),
        team_member_id="tm-1866",
        user_id="admin-1866",
    )


@pytest.fixture
def conversation_repo():
    repo = MagicMock()
    repo.read = AsyncMock(return_value=_conversation_doc())
    repo.query = AsyncMock(return_value=[])
    repo.patch = AsyncMock()
    return repo


def test_conversation_document_exposes_override_storage_fields():
    fields = (
        ConversationDocument.model_fields
        if hasattr(ConversationDocument, "model_fields")
        else ConversationDocument.__fields__
    )

    assert "conversation_agent_override" in fields
    assert "conversation_agent_override_at" in fields
    assert "conversation_agent_override_by" in fields


@pytest.mark.asyncio
async def test_set_override_hydrates_cold_cache_validates_and_patches_fields(
    tenant_ctx,
    conversation_repo,
):
    import src.multi_tenant.admin_conversation_api as module

    module._conversation_repo = conversation_repo
    agent_defn = SimpleNamespace(tier_gate="free")
    effective_config = SimpleNamespace(enabled=True)
    skill_service = MagicMock()
    skill_service._loaded_tenants = set()
    skill_service.load_tenant_bindings = AsyncMock()
    skill_service.list_bindings.return_value = [
        {"tenant_id": "tenant-1866", "agent_id": "sales", "skill_id": "sales:search-products"}
    ]

    with (
        patch("src.agents.plugins.registry.PluginAgentRegistry") as Registry,
        patch("src.agents.plugins.bindings.SkillBindingService") as BindingService,
        patch("src.agents.plugins.overlay.resolve_effective_config", return_value=effective_config),
        patch("src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository") as OverlayRepo,
        patch("src.agents.plugins.events.emit_invocation") as emit_invocation,
    ):
        Registry.get_instance.return_value.get.return_value = agent_defn
        BindingService.get_instance.return_value = skill_service
        OverlayRepo.return_value.get_overlay = AsyncMock(return_value={"enabled": True, "visibility_scope": "public"})

        from src.multi_tenant.admin_conversation_api import AgentOverrideRequest, set_agent_override

        result = await set_agent_override(
            "conv-1866",
            request=AgentOverrideRequest(agent_id="sales"),
            ctx=tenant_ctx,
        )

    skill_service.load_tenant_bindings.assert_awaited_once_with("tenant-1866")
    skill_service.list_bindings.assert_called_once_with("tenant-1866", agent_id="sales")
    conversation_repo.patch.assert_awaited_once()
    patch_kwargs = conversation_repo.patch.call_args.kwargs
    assert patch_kwargs["tenant_id"] == "tenant-1866"
    assert patch_kwargs["document_id"] == "conv-1866"
    operations_by_path = {op["path"]: op["value"] for op in patch_kwargs["operations"]}
    assert operations_by_path["/conversation_agent_override"] == "sales"
    assert operations_by_path["/conversation_agent_override_at"] is not None
    assert operations_by_path["/conversation_agent_override_by"] == "tm-1866"
    assert operations_by_path["/last_activity_at"] == operations_by_path["/conversation_agent_override_at"]
    emit_invocation.assert_called_once()
    assert emit_invocation.call_args.kwargs["target_agent_id"] == "sales"
    assert emit_invocation.call_args.kwargs["result_class"] == "override_set"
    assert result.conversation_id == "conv-1866"
    assert result.agent_id == "sales"
    assert result.set_by == "tm-1866"


@pytest.mark.asyncio
async def test_clear_override_patches_override_fields_to_none(
    tenant_ctx,
    conversation_repo,
):
    import src.multi_tenant.admin_conversation_api as module

    module._conversation_repo = conversation_repo
    conversation_repo.read.return_value = _conversation_doc(conversation_agent_override="sales")

    with patch("src.agents.plugins.events.emit_invocation") as emit_invocation:
        from src.multi_tenant.admin_conversation_api import AgentOverrideRequest, set_agent_override

        result = await set_agent_override(
            "conv-1866",
            request=AgentOverrideRequest(agent_id=None),
            ctx=tenant_ctx,
        )

    patch_kwargs = conversation_repo.patch.call_args.kwargs
    operations_by_path = {op["path"]: op["value"] for op in patch_kwargs["operations"]}
    assert operations_by_path["/conversation_agent_override"] is None
    assert operations_by_path["/conversation_agent_override_at"] is None
    assert operations_by_path["/conversation_agent_override_by"] is None
    assert operations_by_path["/last_activity_at"] is not None
    emit_invocation.assert_called_once()
    assert emit_invocation.call_args.kwargs["result_class"] == "override_cleared"
    assert result.agent_id is None
    assert result.set_at is None
    assert result.set_by is None


def test_router_conversation_override_takes_highest_precedence_and_resolves_default_skill():
    registry = PluginAgentRegistry.get_instance()
    registry.load_from_yaml()
    bindings = SkillBindingService.get_instance()
    bindings.create_binding(
        tenant_id="tenant-1866",
        agent_id="sales",
        skill_id="sales:search-products",
    )
    bindings.create_binding(
        tenant_id="tenant-1866",
        agent_id="campaigns",
        skill_id="campaigns:list-active",
    )

    route = IntentRouter().resolve(
        tenant_id="tenant-1866",
        intent="admin_assistance",
        confidence=0.92,
        team_member_role="admin",
        target_agent_id="campaigns",
        tenant_tier="professional",
        conversation_agent_override="sales",
    )

    assert route.target == RouteTarget.PEER_AGENT
    assert route.agent_id == "sales"
    assert route.skill_id == "sales:search-products"
    assert route.error_reason is None


def test_router_failed_conversation_override_falls_through_to_standard_routing():
    registry = PluginAgentRegistry.get_instance()
    registry.load_from_yaml()

    route = IntentRouter().resolve(
        tenant_id="tenant-1866",
        intent="admin_assistance",
        confidence=0.92,
        team_member_role="admin",
        tenant_tier="professional",
        conversation_agent_override="sales",
    )

    assert route.target == RouteTarget.CO_PILOT
    assert route.agent_id is None
    assert route.error_reason is None
