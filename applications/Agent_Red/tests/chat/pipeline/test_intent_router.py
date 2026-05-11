"""IntentRouter unit tests (SPEC-1861, ADR-003).

Tests for the deterministic execution-plan boundary that routes
customer traffic after intent classification.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.agents.plugins.bindings import SkillBindingService
from src.agents.plugins.events import InvocationEventBus
from src.agents.plugins.registry import PluginAgentRegistry
from src.chat.pipeline.intent_router import (
    IntentRouter,
    RouteDecision,
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
# Core routing logic
# ---------------------------------------------------------------------------


class TestCoreRouting:
    """IntentRouter deterministic routing (SPEC-1861)."""

    def test_default_route_is_core_pipeline(self, registry, router):
        """Unknown/standard intents route to CORE_PIPELINE."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.9,
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.agent_id is None
        assert route.fallback_from is None

    def test_escalation_intent_routes_to_escalation(self, registry, router):
        """'escalation' intent routes to ESCALATION."""
        route = router.resolve(
            tenant_id="t-1", intent="escalation", confidence=0.85,
        )
        assert route.target == RouteTarget.ESCALATION
        assert route.confidence == 0.85

    def test_admin_assistance_routes_to_co_pilot(self, registry, router):
        """'admin_assistance' intent routes to CO_PILOT."""
        route = router.resolve(
            tenant_id="t-1", intent="admin_assistance", confidence=0.95,
        )
        assert route.target == RouteTarget.CO_PILOT

    def test_team_member_role_routes_to_co_pilot(self, registry, router):
        """team_member_role present routes to CO_PILOT regardless of intent."""
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            team_member_role="admin",
        )
        assert route.target == RouteTarget.CO_PILOT

    def test_greeting_routes_to_core_pipeline(self, registry, router):
        """'greeting' intent (no routing rule) goes to CORE_PIPELINE."""
        route = router.resolve(
            tenant_id="t-1", intent="greeting", confidence=0.99,
        )
        assert route.target == RouteTarget.CORE_PIPELINE


# ---------------------------------------------------------------------------
# Peer agent routing via tenant overlay
# ---------------------------------------------------------------------------


class TestTenantOverlayRouting:
    """Tenant overlay intent_routes override registry defaults."""

    def test_tenant_overlay_routes_to_peer_agent(self, registry, router, binding_svc):
        """Overlay intent_routes with binding routes to PEER_AGENT."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay,
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"
        assert route.skill_id == "sales:search-products"

    def test_peer_agent_without_binding_falls_back(self, registry, router):
        """Peer routing without binding falls back to CORE_PIPELINE."""
        overlay = {
            "sales": {
                "enabled": True,
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay,
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.fallback_from == "sales"

    def test_peer_agent_disabled_by_overlay_falls_back(self, registry, router, binding_svc):
        """Disabled agent in overlay falls back to CORE_PIPELINE."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": False,  # Agent disabled
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay,
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.fallback_from == "sales"


# ---------------------------------------------------------------------------
# Registry routing rules
# ---------------------------------------------------------------------------


class TestRegistryRoutingRules:
    """Registry routing_rules provide default suggestions."""

    def test_registry_routing_rules_loaded(self, registry):
        """agents.yaml routing_rules are parsed and queryable."""
        rule = registry.get_routing_rule("product_question")
        assert rule is not None
        assert rule["suggested_peer"] == "sales"
        assert rule["skill"] == "sales:search-products"

    def test_registry_rules_suggest_peer_with_binding(self, registry, router, binding_svc):
        """Registry rule suggestion activates with binding."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"

    def test_registry_rules_without_binding_falls_through(self, registry, router):
        """Registry suggestion without binding silently falls to CORE_PIPELINE."""
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
        )
        # No binding → registry suggestion fails silently → CORE_PIPELINE
        assert route.target == RouteTarget.CORE_PIPELINE

    def test_no_routing_rule_for_unknown_intent(self, registry):
        """No routing rule for intents without default mappings."""
        assert registry.get_routing_rule("greeting") is None
        assert registry.get_routing_rule("nonexistent") is None


# ---------------------------------------------------------------------------
# Denial events and fallback
# ---------------------------------------------------------------------------


class TestDenialAndFallback:
    """Fallback and denial event emission."""

    def test_fallback_emits_denial_event(self, registry, router):
        """Failed peer routing emits a denial invocation event."""
        bus = InvocationEventBus.get_instance()
        bus.enable_buffer()

        overlay = {
            "sales": {
                "enabled": True,
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay,
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.fallback_from == "sales"

        events = bus.get_buffered_events()
        assert len(events) >= 1
        assert events[0].result_class == "denied"
        assert events[0].target_agent_id == "sales"

    def test_route_decision_fields(self, registry, router, binding_svc):
        """RouteDecision contains all expected fields."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.75,
        )
        assert isinstance(route, RouteDecision)
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"
        assert route.skill_id == "sales:search-products"
        assert route.confidence == 0.75
        assert route.fallback_from is None


# ---------------------------------------------------------------------------
# Tier-gate enforcement (Phase 4b WP1)
# ---------------------------------------------------------------------------


class TestTierGateEnforcement:
    """Tier-gate denies under-tiered tenants at the router level."""

    def test_professional_agent_denied_for_starter_tier(self, registry, router, binding_svc):
        """Starter-tier tenant cannot route to professional-gated agent."""
        # zendesk is professional-gated in agents.yaml
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="zendesk",
            skill_id="zendesk:list-tickets",
        )
        overlay = {
            "zendesk": {"enabled": True},
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, tenant_tier="starter",
            target_agent_id="zendesk", team_member_role="admin",
        )
        assert route.target == RouteTarget.ERROR
        assert route.fallback_from == "zendesk"

    def test_professional_agent_allowed_for_professional_tier(self, registry, router, binding_svc):
        """Professional-tier tenant can route to professional-gated agent."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="zendesk",
            skill_id="zendesk:list-tickets",
        )
        overlay = {
            "zendesk": {"enabled": True},
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, tenant_tier="professional",
            target_agent_id="zendesk", team_member_role="admin",
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "zendesk"

    def test_tier_gate_none_does_not_block(self, registry, router, binding_svc):
        """When tenant_tier is None, tier gate is not enforced (backward compat)."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            tenant_tier=None,
        )
        assert route.target == RouteTarget.PEER_AGENT

    def test_registry_routing_rules_enforce_tier_gate(self, registry, router, binding_svc):
        """Registry routing_rules branch enforces tier gate (regression: was missing context)."""
        # sales is professional-gated; create binding so only tier blocks
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        # Registry routes product_question -> sales (professional-gated)
        # Starter tenant should be denied at tier gate
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            tenant_tier="starter",
        )
        # Should NOT route to sales — tier gate blocks it
        assert route.target == RouteTarget.CORE_PIPELINE

    def test_registry_routing_rules_pass_tier_gate(self, registry, router, binding_svc):
        """Registry routing_rules allows routing when tier is sufficient."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            tenant_tier="professional",
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"


# ---------------------------------------------------------------------------
# Domain-scope enforcement (Phase 4b WP4)
# ---------------------------------------------------------------------------


class TestDomainScopeEnforcement:
    """Private-scope agents require matching staff_domain_tags."""

    def test_private_agent_denied_for_untagged_caller(self, registry, router, binding_svc):
        """Caller with no domain tags is denied access to private-scope agent."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "visibility_scope": "private",
                "staff_domain_tags": ["sales-dept"],
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, staff_domain_tags=(),
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.fallback_from == "sales"

    def test_private_agent_denied_for_none_tags(self, registry, router, binding_svc):
        """Caller with None domain tags is denied access to private-scope agent."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "visibility_scope": "private",
                "staff_domain_tags": ["sales-dept"],
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, staff_domain_tags=None,
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.fallback_from == "sales"

    def test_private_agent_denied_for_wrong_tags(self, registry, router, binding_svc):
        """Caller with non-matching tags is denied access to private-scope agent."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "visibility_scope": "private",
                "staff_domain_tags": ["sales-dept"],
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, staff_domain_tags=("support-dept",),
        )
        assert route.target == RouteTarget.CORE_PIPELINE
        assert route.fallback_from == "sales"

    def test_private_agent_allowed_for_matching_tags(self, registry, router, binding_svc):
        """Caller with matching tags can access private-scope agent."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "visibility_scope": "private",
                "staff_domain_tags": ["sales-dept"],
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, staff_domain_tags=("sales-dept",),
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"

    def test_public_agent_accessible_without_tags(self, registry, router, binding_svc):
        """Public-scope agent (default) is accessible without domain tags."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "visibility_scope": "public",
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, staff_domain_tags=(),
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"

    def test_private_scope_no_overlay_tags_denies_all(self, registry, router, binding_svc):
        """Private scope with empty overlay tags denies all callers."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        overlay = {
            "sales": {
                "enabled": True,
                "visibility_scope": "private",
                "staff_domain_tags": [],
                "custom_metadata": {
                    "intent_routes": {
                        "product_question": {
                            "agent_id": "sales",
                            "skill_id": "sales:search-products",
                        },
                    },
                },
            },
        }
        # Even a caller with tags should be denied when overlay scope is private
        # but overlay itself has no tags (deny-by-default)
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.8,
            overlay_store=overlay, staff_domain_tags=("sales-dept",),
        )
        assert route.target == RouteTarget.CORE_PIPELINE


# ---------------------------------------------------------------------------
# Intent confidence threshold (B2, SPEC-1869)
# ---------------------------------------------------------------------------


class TestIntentConfidenceThreshold:
    """B2: Tenant-configurable IC confidence gating (SPEC-1869)."""

    def test_threshold_disabled_routes_core_pipeline(self, registry, router):
        """threshold=0.0 (default/disabled) never triggers CLARIFICATION."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.1,
            intent_confidence_threshold=0.0,
        )
        assert route.target == RouteTarget.CORE_PIPELINE

    def test_confidence_below_threshold_routes_clarification(self, registry, router):
        """Confidence below threshold routes to CLARIFICATION."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.3,
            intent_confidence_threshold=0.5,
        )
        assert route.target == RouteTarget.CLARIFICATION
        assert route.confidence == 0.3

    def test_confidence_at_threshold_routes_core_pipeline(self, registry, router):
        """Confidence exactly at threshold proceeds (not strict less-than)."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.5,
            intent_confidence_threshold=0.5,
        )
        assert route.target == RouteTarget.CORE_PIPELINE

    def test_confidence_above_threshold_routes_core_pipeline(self, registry, router):
        """Confidence above threshold proceeds normally."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.8,
            intent_confidence_threshold=0.5,
        )
        assert route.target == RouteTarget.CORE_PIPELINE

    def test_escalation_bypasses_threshold(self, registry, router):
        """Escalation intent routes to ESCALATION regardless of threshold."""
        route = router.resolve(
            tenant_id="t-1", intent="escalation", confidence=0.1,
            intent_confidence_threshold=0.9,
        )
        assert route.target == RouteTarget.ESCALATION

    def test_co_pilot_bypasses_threshold(self, registry, router):
        """Team member role routes to CO_PILOT regardless of threshold."""
        route = router.resolve(
            tenant_id="t-1", intent="general_inquiry", confidence=0.1,
            team_member_role="admin",
            intent_confidence_threshold=0.9,
        )
        assert route.target == RouteTarget.CO_PILOT

    def test_clarification_has_priority_over_peer_routing(self, registry, router, binding_svc):
        """Low confidence clarifies before attempting peer agent routing."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        route = router.resolve(
            tenant_id="t-1", intent="product_question", confidence=0.2,
            intent_confidence_threshold=0.5,
        )
        assert route.target == RouteTarget.CLARIFICATION

    def test_override_resolves_default_skill(self, registry, router, binding_svc):
        """Conversation override with no skill_id resolves first enabled binding."""
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:search-products",
        )
        binding_svc.create_binding(
            tenant_id="t-1", agent_id="sales",
            skill_id="sales:cart-management",
        )
        route = router.resolve(
            tenant_id="t-1", intent="greeting", confidence=0.9,
            conversation_agent_override="sales",
        )
        assert route.target == RouteTarget.PEER_AGENT
        assert route.agent_id == "sales"
        assert route.skill_id is not None
        assert route.skill_id != ""
