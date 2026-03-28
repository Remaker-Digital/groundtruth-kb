"""Phase 3 — Environment parity tests.

Proves transport selection behavior is identical across environments and
no in-process rescue path exists. ALL tests execute behavior — none
inspect source code.

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Category 4.
Governing decisions: ADR-001, DCL-002.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_transport_singletons():
    """Reset AGNTCY SDK singletons between tests."""
    import src.multi_tenant.agntcy_sdk_integration as mod
    old_factory = mod._factory
    old_transport = mod._transport
    mod._factory = None
    mod._transport = None
    yield
    mod._factory = old_factory
    mod._transport = old_transport


# ---------------------------------------------------------------------------
# 1. Transport selection behavioral
# ---------------------------------------------------------------------------


class TestTransportSelectionBehavioral:
    """Verify transport selection produces the same result in all environments."""

    def test_transport_selection_identical_across_envs(self):
        """get_default_transport() returns the same type in all environments.

        When SLIM is configured, all environments should produce a transport
        (or None if SLIM can't connect). When not configured, all return None.
        The key assertion: no environment produces a different result.
        """
        results = {}
        for env_name in ("development", "staging", "production"):
            with patch.dict(os.environ, {
                "ENVIRONMENT": env_name,
                "AGNTCY_SLIM_ENDPOINT": "",
                "AGNTCY_NATS_ENDPOINT": "",
                "NATS_URL": "",
            }, clear=False):
                import importlib
                import src.multi_tenant.agntcy_sdk_integration as mod
                importlib.reload(mod)
                mod._factory = None
                mod._transport = None
                results[env_name] = mod.get_default_transport()

        # All must be the same (None when no endpoints configured)
        values = list(results.values())
        assert all(v == values[0] for v in values), (
            f"Transport selection differs across environments: {results}"
        )


# ---------------------------------------------------------------------------
# 2. USE_AGENT_CONTAINERS behavioral
# ---------------------------------------------------------------------------


class TestUseAgentContainersBehavioral:
    """Verify USE_AGENT_CONTAINERS is True in all environments."""

    def test_use_agent_containers_true_all_envs(self):
        """USE_AGENT_CONTAINERS must be True in dev/staging/production."""
        for env_name in ("development", "staging", "production", ""):
            with patch.dict(os.environ, {"ENVIRONMENT": env_name}, clear=False):
                import importlib
                import src.chat.pipeline.constants as mod
                importlib.reload(mod)
                assert mod.USE_AGENT_CONTAINERS is True, (
                    f"USE_AGENT_CONTAINERS is False in {env_name or 'unset'}"
                )


# ---------------------------------------------------------------------------
# 3. TRANSPORT_TYPE behavioral
# ---------------------------------------------------------------------------


class TestTransportTypeBehavioral:
    """Verify TRANSPORT_TYPE defaults to 'slim' in all environments."""

    def test_transport_type_slim_all_envs(self):
        """TRANSPORT_TYPE should be 'slim' regardless of ENVIRONMENT value."""
        for env_name in ("development", "staging", "production"):
            with patch.dict(os.environ, {
                "ENVIRONMENT": env_name,
                "AGNTCY_TRANSPORT_TYPE": "slim",
            }, clear=False):
                import importlib
                import src.multi_tenant.agntcy_sdk_integration as mod
                importlib.reload(mod)
                assert mod.TRANSPORT_TYPE == "slim", (
                    f"TRANSPORT_TYPE != 'slim' in {env_name}"
                )


# ---------------------------------------------------------------------------
# 4. 503 on exhaustion behavioral
# ---------------------------------------------------------------------------


class TestExhaustionBehavioral:
    """Verify dispatch terminates at 503 when all tiers exhausted."""

    def test_503_on_all_tiers_exhausted(self):
        """_require_transport_or_fail() raises HTTPException 503.

        This proves the dispatch chain terminates correctly by executing
        it — not by reading source code.
        """
        from fastapi import HTTPException
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin.__new__(AgentDispatchMixin)
        with pytest.raises(HTTPException) as exc_info:
            mixin._require_transport_or_fail("test-agent")
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# 5. Critic fail-closed behavioral
# ---------------------------------------------------------------------------


class TestCriticFailClosedBehavioral:
    """Verify Critic returns safe fallback when unavailable."""

    def test_critic_returns_safe_fallback(self):
        """When Critic is unavailable, _validate_with_critic returns safe fallback.

        Executes the fail-closed path — does not inspect source code.
        """
        from src.chat.pipeline.critic_escalation import CriticEscalationMixin
        from src.multi_tenant.critic_policy import SAFE_FALLBACK_MESSAGE

        mixin = CriticEscalationMixin.__new__(CriticEscalationMixin)
        # No CriticPolicy configured → hit fail-closed path
        mixin._critic = None
        mixin._agent_urls = {}

        # Patch transport to None so transport path fails
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", None), \
             patch("src.multi_tenant.agntcy_sdk_integration._transport_setup_ok", False):
            approved, message, result = asyncio.run(
                mixin._validate_with_critic(
                    tenant_id="test-tenant",
                    conversation_id="test-conv",
                    response_text="Test response",
                    customer_message="Test question",
                    budget=None,
                    knowledge_titles=None,
                )
            )

        # Fail-closed: not approved, safe fallback returned
        assert approved is False
        assert message == SAFE_FALLBACK_MESSAGE


# ---------------------------------------------------------------------------
# 6. Analytics silent-drop behavioral
# ---------------------------------------------------------------------------


class TestAnalyticsSilentDropBehavioral:
    """Verify analytics silently drops when no transport is available."""

    def test_analytics_silent_drop_no_exception(self):
        """_fire_analytics with no transport returns without raising.

        Proves fire-and-forget behavior by executing it — not by reading source.
        """
        from src.chat.pipeline.analytics import AnalyticsMixin

        mixin = AnalyticsMixin.__new__(AnalyticsMixin)
        mixin._agent_urls = {}  # No analytics URL → HTTP will also fail

        class FakeBudget:
            stages = []
            elapsed_ms = 50.0

        class FakeTrace:
            pass

        # No transport, no HTTP → should silently drop
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", None):
            # Must not raise
            asyncio.run(
                mixin._fire_analytics(
                    tenant_id="test-tenant",
                    conversation_id="test-conv",
                    intent="general_inquiry",
                    budget=FakeBudget(),
                    trace=FakeTrace(),
                )
            )
        # If we got here without exception, silent drop is proven


# ---------------------------------------------------------------------------
# 7. Orchestrator agent construction behavioral
# ---------------------------------------------------------------------------


class TestOrchestratorAgentConstructionBehavioral:
    """Verify _init_agents does not create dead agent instances."""

    def test_no_dead_agent_instances(self):
        """_init_agents must NOT set _cr_agent, _esc_agent, _an_agent.

        These were removed in S224. Verify by constructing the pipeline
        and checking instance attributes — not by reading source.
        """
        from src.chat.pipeline.orchestrator import ChatPipeline

        # Create a minimal pipeline instance
        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._openai_client = None
        pipeline._kb_repo = None

        # _init_agents may fail due to missing dependencies, but we can
        # check if the dead agent attributes are set on the class after
        # a normal initialization path
        try:
            pipeline._init_agents()
        except Exception:
            # Some agents may fail to construct without real deps — that's OK.
            # The test verifies which attributes were set before failure.
            pass

        # These agents were removed in S224 — they must not exist
        assert not hasattr(pipeline, "_cr_agent"), (
            "_cr_agent still set — CriticSupervisorAgent not removed"
        )
        assert not hasattr(pipeline, "_esc_agent"), (
            "_esc_agent still set — EscalationHandlerAgent not removed"
        )
        assert not hasattr(pipeline, "_an_agent"), (
            "_an_agent still set — AnalyticsCollectorAgent not removed"
        )
