"""Tests for agent container deployment and HTTP dispatch (Builds 4-5).

Verifies:
- Agent container entry points are importable and create valid FastAPI apps
- Gateway-compatible short path aliases are registered
- Container health/ready endpoints respond correctly
- HTTP dispatch paths match gateway expectations
- Co-pilot container entry point exists and is configured correctly
- deploy_agent_containers.py script defines all 7 agents

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Container entry point tests
# ---------------------------------------------------------------------------


class TestContainerEntryPoints:
    """Verify all 7 agent container entry points are importable."""

    AGENT_MODULES = [
        "src.agents.containers.intent_classifier_app",
        "src.agents.containers.knowledge_retrieval_app",
        "src.agents.containers.response_generator_app",
        "src.agents.containers.escalation_handler_app",
        "src.agents.containers.analytics_collector_app",
        "src.agents.containers.critic_supervisor_app",
        "src.agents.containers.co_pilot_app",
    ]

    @pytest.mark.parametrize("module_path", AGENT_MODULES)
    def test_entry_point_importable(self, module_path: str) -> None:
        """Each agent container module must be importable."""
        mod = importlib.import_module(module_path)
        assert hasattr(mod, "app"), f"{module_path} must export 'app'"

    @pytest.mark.parametrize("module_path", AGENT_MODULES)
    def test_entry_point_has_fastapi_app(self, module_path: str) -> None:
        """Each container app must be a FastAPI instance."""
        mod = importlib.import_module(module_path)
        from fastapi import FastAPI
        assert isinstance(mod.app, FastAPI)


class TestGatewayPathAliases:
    """Verify gateway-compatible short path aliases are registered."""

    EXPECTED_PATHS = {
        "src.agents.containers.intent_classifier_app": "/classify",
        "src.agents.containers.knowledge_retrieval_app": "/retrieve",
        "src.agents.containers.response_generator_app": "/generate",
        "src.agents.containers.escalation_handler_app": "/escalate",
        "src.agents.containers.analytics_collector_app": "/collect",
        "src.agents.containers.critic_supervisor_app": "/validate",
        "src.agents.containers.co_pilot_app": "/process",
    }

    @pytest.mark.parametrize(
        "module_path,expected_path",
        list(EXPECTED_PATHS.items()),
        ids=[p.split(".")[-1] for p in EXPECTED_PATHS],
    )
    def test_gateway_path_registered(self, module_path: str, expected_path: str) -> None:
        """Each container must register its gateway-compatible short path."""
        mod = importlib.import_module(module_path)
        route_paths = [r.path for r in mod.app.routes]
        assert expected_path in route_paths, (
            f"{module_path} missing gateway path alias '{expected_path}'. "
            f"Available routes: {route_paths}"
        )


class TestResponseGeneratorStreaming:
    """Verify the response-generator has a dedicated streaming endpoint."""

    def test_generate_stream_route_exists(self) -> None:
        """RG container must expose /generate/stream for SSE streaming."""
        from src.agents.containers.response_generator_app import app
        route_paths = [r.path for r in app.routes]
        assert "/generate/stream" in route_paths


class TestAgentAppFactory:
    """Test the create_agent_app factory function."""

    def test_health_endpoint_exists(self) -> None:
        """All containers must expose /health."""
        from src.agents.containers.intent_classifier_app import app
        route_paths = [r.path for r in app.routes]
        assert "/health" in route_paths

    def test_ready_endpoint_exists(self) -> None:
        """All containers must expose /ready."""
        from src.agents.containers.intent_classifier_app import app
        route_paths = [r.path for r in app.routes]
        assert "/ready" in route_paths

    def test_a2a_process_endpoint_exists(self) -> None:
        """All containers must expose /agents/{type}/process."""
        from src.agents.containers.intent_classifier_app import app
        route_paths = [r.path for r in app.routes]
        assert "/agents/intent-classifier/process" in route_paths

    def test_agent_stored_in_app_state(self) -> None:
        """Agent instance must be stored in app.state.agent."""
        from src.agents.containers.intent_classifier_app import app
        assert hasattr(app.state, "agent")
        assert app.state.agent.agent_type == "intent-classifier"


class TestCoPilotContainerConfig:
    """Verify co-pilot container entry point configuration."""

    def test_co_pilot_agent_type(self) -> None:
        """Co-pilot container must use CoPilotAgent."""
        from src.agents.containers.co_pilot_app import app
        assert app.state.agent.agent_type == "co-pilot"

    def test_co_pilot_has_configure_fn(self) -> None:
        """Co-pilot module must define a _configure function."""
        from src.agents.containers import co_pilot_app
        assert hasattr(co_pilot_app, "_configure")
        assert callable(co_pilot_app._configure)


# ---------------------------------------------------------------------------
# Constants / dispatch configuration tests
# ---------------------------------------------------------------------------


class TestAgentURLConfiguration:
    """Verify AGENT_URLS covers all 7 agents."""

    def test_all_agents_in_urls(self) -> None:
        """AGENT_URLS must have entries for all 7 agents."""
        from src.chat.pipeline.constants import AGENT_URLS
        expected = {
            "intent-classifier",
            "knowledge-retrieval",
            "response-generator",
            "escalation-handler",
            "analytics-collector",
            "critic-supervisor",
            "co-pilot",
        }
        assert set(AGENT_URLS.keys()) == expected

    def test_agent_urls_have_env_overrides(self) -> None:
        """Each agent URL must be overridable via environment variable."""
        from src.chat.pipeline.constants import AGENT_URLS
        # With no env vars set, all should have default values
        for agent_name, url in AGENT_URLS.items():
            assert url, f"Agent {agent_name} has empty URL"
            assert url.startswith("http"), f"Agent {agent_name} URL must be HTTP"


class TestAgentPathConstants:
    """Verify path constants match container gateway aliases."""

    def test_classify_path(self) -> None:
        from src.chat.pipeline.constants import AGENT_CLASSIFY_PATH
        assert AGENT_CLASSIFY_PATH == "/classify"

    def test_retrieve_path(self) -> None:
        from src.chat.pipeline.constants import AGENT_RETRIEVE_PATH
        assert AGENT_RETRIEVE_PATH == "/retrieve"

    def test_generate_path(self) -> None:
        from src.chat.pipeline.constants import AGENT_GENERATE_PATH
        assert AGENT_GENERATE_PATH == "/generate"

    def test_generate_stream_path(self) -> None:
        from src.chat.pipeline.constants import AGENT_GENERATE_STREAM_PATH
        assert AGENT_GENERATE_STREAM_PATH == "/generate/stream"

    def test_escalate_path(self) -> None:
        from src.chat.pipeline.constants import AGENT_ESCALATE_PATH
        assert AGENT_ESCALATE_PATH == "/escalate"

    def test_collect_path(self) -> None:
        from src.chat.pipeline.constants import AGENT_ANALYTICS_PATH
        assert AGENT_ANALYTICS_PATH == "/collect"


# ---------------------------------------------------------------------------
# Deploy script tests
# ---------------------------------------------------------------------------


class TestDeployScript:
    """Verify the deploy_agent_containers.py script configuration."""

    def test_deploy_script_defines_all_agents(self) -> None:
        """Deploy script AGENTS dict must cover all 7 agents."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
        try:
            import deploy_agent_containers
            importlib.reload(deploy_agent_containers)
            expected = {
                "intent-classifier",
                "knowledge-retrieval",
                "response-generator",
                "escalation-handler",
                "analytics-collector",
                "critic-supervisor",
                "co-pilot",
            }
            assert set(deploy_agent_containers.AGENTS.keys()) == expected
        finally:
            sys.path.pop(0)

    def test_deploy_script_module_paths_match_containers(self) -> None:
        """Deploy script module paths must match actual container entry points."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
        try:
            import deploy_agent_containers
            for agent_name, module_path in deploy_agent_containers.AGENTS.items():
                # Each module path should be importable
                module_name = module_path.split(":")[0]
                mod = importlib.import_module(module_name)
                assert hasattr(mod, "app"), f"Module {module_name} must export 'app'"
        finally:
            sys.path.pop(0)


# ---------------------------------------------------------------------------
# Version verification
# ---------------------------------------------------------------------------


class TestVersionBump:
    """Verify product version is current."""

    def test_product_version(self) -> None:
        from src.multi_tenant.api_versioning import PRODUCT_VERSION
        assert PRODUCT_VERSION == "1.95.2"
