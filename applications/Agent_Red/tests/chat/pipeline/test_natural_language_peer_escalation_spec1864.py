"""Router coverage for natural-language peer escalation (SPEC-1864)."""

from __future__ import annotations

import pytest

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.events import InvocationEventBus
from src.agents.plugins.registry import PluginAgentRegistry
from src.chat.pipeline.intent_router import IntentRouter, RouteTarget

TENANT_ID = "tenant-spec-1864"


@pytest.fixture(autouse=True)
def _reset_services():
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
def router(registry):
    return IntentRouter()


@pytest.fixture
def binding_svc():
    return SkillBindingService.get_instance()


def _bind(agent_id: str, skill_id: str, binding_svc: SkillBindingService) -> None:
    binding_svc.create_binding(
        tenant_id=TENANT_ID,
        agent_id=agent_id,
        skill_id=skill_id,
    )


def test_team_member_transfer_to_sales_routes_to_bound_peer_agent(
    router: IntentRouter,
    binding_svc: SkillBindingService,
) -> None:
    _bind("sales", "sales:search-products", binding_svc)

    route = router.resolve(
        tenant_id=TENANT_ID,
        intent="admin_assistance",
        confidence=0.93,
        team_member_role="admin",
        user_message="transfer to sales",
        tenant_tier="professional",
    )

    assert route.target == RouteTarget.PEER_AGENT
    assert route.agent_id == "sales"
    assert route.skill_id == "sales:search-products"
    assert route.confidence == 0.93


def test_team_member_phrase_resolves_campaigns_display_language(
    router: IntentRouter,
    binding_svc: SkillBindingService,
) -> None:
    _bind("campaigns", "campaigns:list-active", binding_svc)

    route = router.resolve(
        tenant_id=TENANT_ID,
        intent="admin_assistance",
        confidence=0.88,
        team_member_role="admin",
        user_message="let the campaigns agent handle this",
        tenant_tier="professional",
    )

    assert route.target == RouteTarget.PEER_AGENT
    assert route.agent_id == "campaigns"
    assert route.skill_id == "campaigns:list-active"


def test_unbound_team_member_peer_phrase_falls_back_to_co_pilot(
    router: IntentRouter,
) -> None:
    route = router.resolve(
        tenant_id=TENANT_ID,
        intent="admin_assistance",
        confidence=0.82,
        team_member_role="admin",
        user_message="transfer to sales",
        tenant_tier="professional",
    )

    assert route.target == RouteTarget.CO_PILOT
    assert route.agent_id is None
    assert route.skill_id is None
    assert route.fallback_from is None


def test_team_member_phrase_naming_core_agent_stays_co_pilot(
    router: IntentRouter,
    binding_svc: SkillBindingService,
) -> None:
    _bind("sales", "sales:search-products", binding_svc)

    route = router.resolve(
        tenant_id=TENANT_ID,
        intent="admin_assistance",
        confidence=0.79,
        team_member_role="admin",
        user_message="transfer to intent classifier",
        tenant_tier="professional",
    )

    assert route.target == RouteTarget.CO_PILOT
    assert route.agent_id is None
    assert route.skill_id is None


def test_existing_customer_natural_language_fallback_still_routes_peer_agent(
    router: IntentRouter,
    binding_svc: SkillBindingService,
) -> None:
    _bind("sales", "sales:search-products", binding_svc)

    route = router.resolve(
        tenant_id=TENANT_ID,
        intent="general_inquiry",
        confidence=0.91,
        user_message="transfer to sales",
        tenant_tier="professional",
    )

    assert route.target == RouteTarget.PEER_AGENT
    assert route.agent_id == "sales"
    assert route.skill_id == "sales:search-products"
