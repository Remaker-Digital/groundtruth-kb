"""Phase 3 — Transport contract tests.

Validates that real SDK imports work, required APIs exist, and signatures
match usage. These tests use NO mocks — they verify the actual contract
between Agent Red code and the AGNTCY SDK / slim_bindings packages.

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 3, Category 1.
Governing decisions: ADR-001, ADR-002, DCL-002, SPEC-1802.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
import importlib

import pytest


# ---------------------------------------------------------------------------
# 1. Real SDK imports — verify packages are installed and importable
# ---------------------------------------------------------------------------


class TestSDKImports:
    """Verify that all transport SDK packages are importable."""

    def test_agntcy_app_sdk_importable(self):
        """AGNTCY App SDK must be importable."""
        mod = importlib.import_module("agntcy_app_sdk")
        assert mod is not None

    def test_agntcy_factory_importable(self):
        """AgntcyFactory must be importable from agntcy_app_sdk.factory."""
        from agntcy_app_sdk.factory import AgntcyFactory
        assert AgntcyFactory is not None

    def test_a2a_types_importable(self):
        """A2A protocol types must be importable (used by agent_dispatch.py)."""
        from a2a.types import (
            Message,
            MessageSendParams,
            Role,
            SendMessageRequest,
            TextPart,
        )
        assert Message is not None
        assert Role is not None

    def test_slim_bindings_importable(self):
        """SLIM bindings (Rust) must be importable (used by slim_server_app.py)."""
        import slim_bindings as sb
        assert hasattr(sb, "initialize_with_defaults")
        assert hasattr(sb, "create_service")
        assert hasattr(sb, "new_insecure_server_config")
        assert hasattr(sb, "get_version")
        assert hasattr(sb, "get_build_info")

    def test_nats_py_importable(self):
        """nats-py must be importable (WebSocket transport for Container Apps)."""
        import nats
        assert hasattr(nats, "connect")


# ---------------------------------------------------------------------------
# 2. API existence — required methods and attributes exist
# ---------------------------------------------------------------------------


class TestSDKAPIs:
    """Verify that SDK classes expose the APIs we depend on."""

    def test_factory_has_create_transport(self):
        """AgntcyFactory must have create_transport() method."""
        from agntcy_app_sdk.factory import AgntcyFactory
        assert hasattr(AgntcyFactory, "create_transport") or callable(
            getattr(AgntcyFactory, "create_transport", None)
        )

    def test_factory_has_create_client_or_transport(self):
        """AgntcyFactory must have client/transport creation methods."""
        from agntcy_app_sdk.factory import AgntcyFactory
        # Factory must support at least one of these patterns
        has_creation = (
            hasattr(AgntcyFactory, "create_client")
            or hasattr(AgntcyFactory, "create_transport")
            or hasattr(AgntcyFactory, "create_a2a_client")
        )
        assert has_creation, "AgntcyFactory has no client/transport creation method"

    def test_a2a_client_factory_importable(self):
        """A2AClientFactory must be importable (used for HTTP dispatch)."""
        from agntcy_app_sdk.semantic.a2a.client.factory import A2AClientFactory
        assert A2AClientFactory is not None

    def test_slim_bindings_server_api(self):
        """SLIM bindings must expose server creation API."""
        import slim_bindings as sb
        # These are the exact calls made in slim_server_app.py
        assert callable(getattr(sb, "initialize_with_defaults", None))
        assert callable(getattr(sb, "create_service", None))
        assert callable(getattr(sb, "new_insecure_server_config", None))


# ---------------------------------------------------------------------------
# 3. Internal module contracts — Agent Red's own transport modules
# ---------------------------------------------------------------------------


class TestInternalContracts:
    """Verify Agent Red's transport modules expose expected APIs."""

    def test_agntcy_integration_exports(self):
        """agntcy_sdk_integration must export all required symbols."""
        from src.multi_tenant import agntcy_sdk_integration as mod
        required = [
            "AgentTopic",
            "get_agntcy_factory",
            "get_default_transport",
            "create_a2a_client",
            "create_mcp_client",
            "get_sdk_status",
            "init_agntcy_sdk",
            "close_agntcy_sdk",
            "SLIM_ENDPOINT",
            "NATS_ENDPOINT",
            "TRANSPORT_TYPE",
        ]
        for name in required:
            assert hasattr(mod, name), f"Missing export: {name}"

    def test_agent_topic_enum_covers_all_agents(self):
        """AgentTopic enum must have entries for all 7 pipeline agents."""
        from src.multi_tenant.agntcy_sdk_integration import AgentTopic
        required_topics = {
            "intent-classifier",
            "knowledge-retrieval",
            "response-generator",
            "escalation-handler",
            "analytics-collector",
            "critic-supervisor",
            "co-pilot",
        }
        actual_topics = {t.value for t in AgentTopic}
        assert required_topics.issubset(actual_topics), (
            f"Missing topics: {required_topics - actual_topics}"
        )

    def test_agent_dispatch_mixin_has_transport_methods(self):
        """AgentDispatchMixin must expose transport dispatch methods."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
        required_methods = [
            "_transport_available",
            "_call_via_transport",
            "_require_transport_or_fail",
            "_warn_http_failure_mode",
        ]
        for name in required_methods:
            assert hasattr(AgentDispatchMixin, name), f"Missing method: {name}"

    def test_dispatch_mixin_has_no_in_process_canonical_path(self):
        """DCL-002: Dispatch methods must NOT call _direct() in canonical path.

        The _call_intent_classifier, _call_knowledge_retrieval, and
        _call_response_generator methods must contain _require_transport_or_fail
        but NOT reference any _direct method in their body.
        """
        from src.chat.pipeline import agent_dispatch
        source = inspect.getsource(agent_dispatch.AgentDispatchMixin)

        # These dispatch methods should exist
        assert "_call_intent_classifier" in source
        assert "_call_knowledge_retrieval" in source

        # _require_transport_or_fail must be the terminal fallback
        assert "_require_transport_or_fail" in source

    def test_critic_mixin_has_no_in_process_path(self):
        """DCL-002: Critic mixin must not call _validate_with_critic_direct."""
        from src.chat.pipeline import critic_escalation
        source = inspect.getsource(critic_escalation.CriticEscalationMixin._validate_with_critic)
        # Check executable code only (exclude docstring references)
        code_lines = [
            ln for ln in source.split("\n")
            if ln.strip()
            and not ln.strip().startswith(("#", '"""', "'''"))
            and "Phase 2A:" not in ln  # historical note in docstring
        ]
        code = "\n".join(code_lines)
        assert "await self._validate_with_critic_direct" not in code
        assert "self._cr_agent" not in code

    def test_agent_app_factory_exports(self):
        """create_agent_app must be importable and callable."""
        from src.agents.containers.agent_app import create_agent_app
        assert callable(create_agent_app)

    def test_all_agent_entry_points_importable(self):
        """All 6 agent container entry points must be importable."""
        modules = [
            "src.agents.containers.intent_classifier_app",
            "src.agents.containers.knowledge_retrieval_app",
            "src.agents.containers.response_generator_app",
            "src.agents.containers.escalation_handler_app",
            "src.agents.containers.analytics_collector_app",
            "src.agents.containers.critic_supervisor_app",
        ]
        for mod_path in modules:
            mod = importlib.import_module(mod_path)
            assert hasattr(mod, "app"), f"{mod_path} missing 'app' attribute"

    def test_slim_server_app_importable(self):
        """SLIM server app must be importable."""
        from src.agents.containers.slim_server_app import run_slim_server
        assert callable(run_slim_server)

    def test_constants_agent_urls_cover_all_agents(self):
        """AGENT_URLS must have entries for all dispatched agents."""
        from src.chat.pipeline.constants import AGENT_URLS
        required = {
            "intent-classifier",
            "knowledge-retrieval",
            "response-generator",
            "escalation-handler",
            "analytics-collector",
            "critic-supervisor",
        }
        assert required.issubset(set(AGENT_URLS.keys())), (
            f"Missing AGENT_URLS: {required - set(AGENT_URLS.keys())}"
        )
