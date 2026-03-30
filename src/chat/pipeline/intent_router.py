"""IntentRouter — execution-plan boundary after intent classification (ADR-003).

Deterministic routing engine that maps IC output + tenant config to an
execution route: core_pipeline, escalation, co_pilot, or peer_agent.

Resolution order (SPEC-1861):
  1. team_member_role present OR admin_assistance intent → CO_PILOT
  2. escalation intent → ESCALATION
  3. Tenant overlay custom_metadata["intent_routes"] override → verify peer
  4. Registry routing_rules default suggestion → verify peer
  5. Default → CORE_PIPELINE

Safety guarantee: all existing traffic routes to CORE_PIPELINE by default.
Peer routing only activates with explicit tenant overlay config + skill binding.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RouteTarget(str, Enum):
    """Execution route targets (ADR-003)."""

    CORE_PIPELINE = "core_pipeline"
    ESCALATION = "escalation"
    CO_PILOT = "co_pilot"
    PEER_AGENT = "peer_agent"
    CLARIFICATION = "clarification"  # B2: IC confidence below tenant threshold
    ERROR = "error"  # Explicit target verification failure (SPEC-1862)


@dataclass(frozen=True)
class RouteDecision:
    """Immutable result of IntentRouter.resolve().

    target:        which execution branch to take
    agent_id:      peer agent to dispatch to (only for PEER_AGENT)
    skill_id:      primary skill for the peer agent (only for PEER_AGENT)
    confidence:    IC confidence score (passed through for trace)
    fallback_from: if peer routing was attempted but failed, records what
                   was tried before falling back to CORE_PIPELINE
    """

    target: RouteTarget
    agent_id: str | None = None
    skill_id: str | None = None
    confidence: float = 0.0
    fallback_from: str | None = None
    error_reason: str | None = None  # Only for ERROR target (SPEC-1862)


# Intent constants (match src/chat/pipeline/constants.py)
_ESCALATION_INTENT = "escalation"
_ADMIN_ASSISTANCE_INTENT = "admin_assistance"


class IntentRouter:
    """Deterministic execution-plan router (ADR-003, SPEC-1861).

    Routes customer traffic after intent classification. Does NOT use
    an LLM — routing is rule-based from tenant config and registry defaults.
    """

    def resolve(
        self,
        *,
        tenant_id: str,
        intent: str,
        confidence: float,
        team_member_role: str | None = None,
        target_agent_id: str | None = None,
        overlay_store: dict[str, dict[str, Any]] | None = None,
        tenant_tier: str | None = None,
        staff_domain_tags: tuple[str, ...] | None = None,
        intent_confidence_threshold: float = 0.0,
    ) -> RouteDecision:
        """Determine execution route from IC result + tenant config.

        Args:
            tenant_id: current tenant
            intent: IC-classified intent string
            confidence: IC confidence score (0.0-1.0)
            team_member_role: if set, caller is an authenticated team member
            target_agent_id: explicit peer agent target (team members only, SPEC-1862)
            overlay_store: tenant agent overlays (agent_id -> overlay dict)
        """
        # 1a. Team member with explicit target → try PEER_AGENT, ERROR on failure
        if team_member_role and target_agent_id:
            decision = self._try_peer_route(
                tenant_id=tenant_id,
                agent_id=target_agent_id,
                skill_id=None,
                confidence=confidence,
                overlay_store=overlay_store,
                tenant_tier=tenant_tier,
                staff_domain_tags=staff_domain_tags,
            )
            if decision.target == RouteTarget.PEER_AGENT:
                return decision
            # Explicit target failed — return ERROR, not CO_PILOT fallback
            return RouteDecision(
                target=RouteTarget.ERROR,
                agent_id=target_agent_id,
                confidence=confidence,
                fallback_from=target_agent_id,
                error_reason=decision.fallback_from or "agent_verification_failed",
            )

        # 1b. Team member without target or admin_assistance → CO_PILOT
        if team_member_role or intent == _ADMIN_ASSISTANCE_INTENT:
            return RouteDecision(
                target=RouteTarget.CO_PILOT,
                confidence=confidence,
            )

        # 2. Escalation → ESCALATION
        if intent == _ESCALATION_INTENT:
            return RouteDecision(
                target=RouteTarget.ESCALATION,
                confidence=confidence,
            )

        # 2b. Intent confidence threshold gating (B2)
        # When tenant has set a threshold and IC confidence is below it,
        # route to CLARIFICATION instead of proceeding with uncertain intent.
        # Disabled when threshold is 0.0 (default).
        if (
            intent_confidence_threshold > 0.0
            and confidence < intent_confidence_threshold
            and intent != _ESCALATION_INTENT  # escalation always proceeds
        ):
            logger.info(
                "IntentRouter: confidence %.2f below threshold %.2f for tenant %s",
                confidence, intent_confidence_threshold, tenant_id,
            )
            return RouteDecision(
                target=RouteTarget.CLARIFICATION,
                confidence=confidence,
            )

        # 3. Tenant overlay intent_routes (takes precedence over registry)
        if overlay_store:
            for _agent_id, overlay in overlay_store.items():
                intent_routes = (overlay.get("custom_metadata") or {}).get(
                    "intent_routes", {}
                )
                if intent in intent_routes:
                    route_cfg = intent_routes[intent]
                    peer_id = route_cfg.get("agent_id") or route_cfg.get("suggested_peer")
                    skill_id = route_cfg.get("skill_id") or route_cfg.get("skill")
                    if peer_id:
                        decision = self._try_peer_route(
                            tenant_id=tenant_id,
                            agent_id=peer_id,
                            skill_id=skill_id,
                            confidence=confidence,
                            overlay_store=overlay_store,
                            tenant_tier=tenant_tier,
                            staff_domain_tags=staff_domain_tags,
                        )
                        if decision.target == RouteTarget.PEER_AGENT:
                            return decision
                        # Peer failed verification — fall through with fallback recorded
                        return RouteDecision(
                            target=RouteTarget.CORE_PIPELINE,
                            confidence=confidence,
                            fallback_from=peer_id,
                        )

        # 4. Registry routing_rules defaults
        try:
            from src.agents.plugins.registry import PluginAgentRegistry
            reg = PluginAgentRegistry.get_instance()
            rule = reg.get_routing_rule(intent)
            if rule:
                peer_id = rule.get("suggested_peer")
                skill_id = rule.get("skill")
                if peer_id:
                    decision = self._try_peer_route(
                        tenant_id=tenant_id,
                        agent_id=peer_id,
                        skill_id=skill_id,
                        confidence=confidence,
                        overlay_store=overlay_store,
                        tenant_tier=tenant_tier,
                        staff_domain_tags=staff_domain_tags,
                    )
                    if decision.target == RouteTarget.PEER_AGENT:
                        return decision
                    # Registry suggestion failed — fall through silently
                    # (registry rules are suggestions, not mandates)
        except Exception:
            logger.debug("Registry routing_rules lookup failed", exc_info=True)

        # 5. Default → CORE_PIPELINE
        return RouteDecision(
            target=RouteTarget.CORE_PIPELINE,
            confidence=confidence,
        )

    def _try_peer_route(
        self,
        *,
        tenant_id: str,
        agent_id: str,
        skill_id: str | None,
        confidence: float,
        overlay_store: dict[str, dict[str, Any]] | None,
        tenant_tier: str | None = None,
        staff_domain_tags: tuple[str, ...] | None = None,
    ) -> RouteDecision:
        """Attempt to route to a peer agent with full verification.

        Checks: agent exists in registry, tenant tier meets agent tier_gate,
        agent enabled for tenant, skill binding exists (deny-by-default).
        Emits denial event if verification fails.
        """
        try:
            from src.agents.plugins.registry import PluginAgentRegistry
            from src.agents.plugins.overlay import resolve_effective_config
            from src.agents.plugins.bindings import SkillBindingService

            reg = PluginAgentRegistry.get_instance()

            # Agent must exist in registry
            agent_defn = reg.get(agent_id)
            if agent_defn is None:
                logger.warning("IntentRouter: agent %s not in registry", agent_id)
                self._emit_denial(tenant_id, agent_id, skill_id, "agent_not_in_registry")
                return RouteDecision(
                    target=RouteTarget.CORE_PIPELINE,
                    confidence=confidence,
                    fallback_from=agent_id,
                )

            # Tier-gate enforcement (Phase 4b WP1)
            tier_gate = getattr(agent_defn, "tier_gate", None)
            if tier_gate and tier_gate != "free" and tenant_tier:
                tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
                if tier_order.get(str(tenant_tier), 0) < tier_order.get(tier_gate, 0):
                    logger.info(
                        "IntentRouter: agent %s tier-gated (%s) for tenant tier %s",
                        agent_id, tier_gate, tenant_tier,
                    )
                    self._emit_denial(tenant_id, agent_id, skill_id, "tier_gate_denied")
                    return RouteDecision(
                        target=RouteTarget.CORE_PIPELINE,
                        confidence=confidence,
                        fallback_from=agent_id,
                    )

            # Agent must be enabled for this tenant (overlay check)
            config = resolve_effective_config(
                agent_defn,
                overlay=(overlay_store or {}).get(agent_id),
            )
            if not config.enabled:
                logger.info("IntentRouter: agent %s disabled for tenant %s", agent_id, tenant_id)
                self._emit_denial(tenant_id, agent_id, skill_id, "agent_disabled_by_overlay")
                return RouteDecision(
                    target=RouteTarget.CORE_PIPELINE,
                    confidence=confidence,
                    fallback_from=agent_id,
                )

            # Domain-scope enforcement (Phase 4b WP4)
            # Private-scope agents require matching staff_domain_tags.
            # Fail-closed: untagged callers (empty tuple) are denied.
            overlay_data = (overlay_store or {}).get(agent_id) or {}
            visibility_scope = overlay_data.get("visibility_scope", "public")
            if visibility_scope == "private":
                overlay_domain_tags = set(overlay_data.get("staff_domain_tags", []))
                caller_domain_tags = set(staff_domain_tags or ())
                # Deny-by-default for private scope:
                # - Caller has no tags → denied
                # - Overlay has no required tags → denied (not yet configured)
                # - Tags exist on both sides but no intersection → denied
                if (not caller_domain_tags
                        or not overlay_domain_tags
                        or not (caller_domain_tags & overlay_domain_tags)):
                    logger.info(
                        "IntentRouter: agent %s domain-scoped (private), "
                        "caller tags %s do not match overlay tags %s",
                        agent_id, caller_domain_tags, overlay_domain_tags,
                    )
                    self._emit_denial(tenant_id, agent_id, skill_id, "domain_scope_denied")
                    return RouteDecision(
                        target=RouteTarget.CORE_PIPELINE,
                        confidence=confidence,
                        fallback_from=agent_id,
                    )

            # Skill binding must exist (deny-by-default)
            svc = SkillBindingService.get_instance()
            if skill_id:
                binding = svc.get_binding(tenant_id, agent_id, skill_id)
                if binding is None or not binding.get("enabled", True):
                    logger.info(
                        "IntentRouter: no binding for %s/%s/%s",
                        tenant_id, agent_id, skill_id,
                    )
                    self._emit_denial(tenant_id, agent_id, skill_id, "no_binding")
                    return RouteDecision(
                        target=RouteTarget.CORE_PIPELINE,
                        confidence=confidence,
                        fallback_from=agent_id,
                    )
            else:
                # No specific skill — check tenant has ANY binding for this agent
                bindings = svc.list_bindings(tenant_id, agent_id=agent_id)
                if not bindings:
                    logger.info(
                        "IntentRouter: no bindings for %s/%s",
                        tenant_id, agent_id,
                    )
                    self._emit_denial(tenant_id, agent_id, None, "no_binding")
                    return RouteDecision(
                        target=RouteTarget.CORE_PIPELINE,
                        confidence=confidence,
                        fallback_from=agent_id,
                    )

            # All checks passed
            return RouteDecision(
                target=RouteTarget.PEER_AGENT,
                agent_id=agent_id,
                skill_id=skill_id,
                confidence=confidence,
            )

        except Exception:
            logger.debug(
                "IntentRouter: peer route verification failed for %s",
                agent_id, exc_info=True,
            )
            return RouteDecision(
                target=RouteTarget.CORE_PIPELINE,
                confidence=confidence,
                fallback_from=agent_id,
            )

    @staticmethod
    def _emit_denial(
        tenant_id: str,
        agent_id: str,
        skill_id: str | None,
        reason: str,
    ) -> None:
        """Emit an invocation event for a denied peer route attempt."""
        try:
            from src.agents.plugins.events import emit_invocation
            emit_invocation(
                trace_id="",
                invoker="intent-router",
                target_agent_id=agent_id,
                skill_id=skill_id or "",
                tenant_id=tenant_id,
                conversation_id="",
                result_class="denied",
                policy_verdict=reason,
            )
        except Exception:
            logger.debug("Failed to emit denial event", exc_info=True)
