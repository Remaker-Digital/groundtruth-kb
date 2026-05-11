"""Tests for AGENTS specs — agent class existence, methods, and configuration.

Covers 5 specs:
  - SPEC-1396: AnalyticsCollectorAgent class exists in analytics_collector.py
  - SPEC-1399: base.py has process method on AgentRedBaseAgent
  - SPEC-1407: intent_classifier.py uses env var AZURE_IC_MODEL (default: gpt-4o-mini)
  - SPEC-1411: ResponseGeneratorAgent class exists in response_generator.py
  - SPEC-1414: response_generator.py has generate_stream method

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect


class TestAnalyticsCollectorAgent:
    """SPEC-1396: AnalyticsCollectorAgent class in analytics_collector.py."""

    def test_class_exists(self):
        from src.agents.analytics_collector import AnalyticsCollectorAgent

        assert AnalyticsCollectorAgent is not None

    def test_inherits_from_base_agent(self):
        from src.agents.analytics_collector import AnalyticsCollectorAgent
        from src.agents.base import AgentRedBaseAgent

        assert issubclass(AnalyticsCollectorAgent, AgentRedBaseAgent)

    def test_can_be_instantiated(self):
        from src.agents.analytics_collector import AnalyticsCollectorAgent

        agent = AnalyticsCollectorAgent()
        assert agent is not None

    def test_has_process_method(self):
        from src.agents.analytics_collector import AnalyticsCollectorAgent

        assert hasattr(AnalyticsCollectorAgent, "process")
        assert callable(getattr(AnalyticsCollectorAgent, "process"))


class TestBaseAgentProcess:
    """SPEC-1399: base.py has process method on AgentRedBaseAgent."""

    def test_process_method_exists(self):
        from src.agents.base import AgentRedBaseAgent

        assert hasattr(AgentRedBaseAgent, "process")

    def test_process_is_abstract(self):
        from src.agents.base import AgentRedBaseAgent

        # process should be an abstract method (decorated with @abstractmethod)
        assert getattr(AgentRedBaseAgent.process, "__isabstractmethod__", False)

    def test_process_signature_has_payload_and_headers(self):
        from src.agents.base import AgentRedBaseAgent

        sig = inspect.signature(AgentRedBaseAgent.process)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "payload" in params
        assert "headers" in params

    def test_process_is_async(self):
        from src.agents.base import AgentRedBaseAgent

        assert inspect.iscoroutinefunction(AgentRedBaseAgent.process)


class TestIntentClassifierModel:
    """SPEC-1407: intent_classifier.py uses env var AZURE_IC_MODEL (default: gpt-4o-mini)."""

    def test_azure_ic_model_constant_exists(self):
        from src.agents.intent_classifier import AZURE_IC_MODEL

        assert AZURE_IC_MODEL is not None

    def test_azure_ic_model_default_is_gpt_4o_mini(self):
        """Default value when AZURE_IC_MODEL env var is not set."""
        import os
        from unittest.mock import patch

        # Temporarily ensure the env var is not set, then reimport
        with patch.dict(os.environ, {}, clear=False):
            # Remove AZURE_IC_MODEL if present
            env_copy = os.environ.copy()
            env_copy.pop("AZURE_IC_MODEL", None)
            with patch.dict(os.environ, env_copy, clear=True):
                # The default is already evaluated at import time, so we
                # verify the current value matches expectations.
                # If the env var is not set in the test environment,
                # the default should be gpt-4o-mini.
                from src.agents.intent_classifier import AZURE_IC_MODEL

                # Either the env var is set (and we test that path) or
                # the default is gpt-4o-mini
                if "AZURE_IC_MODEL" not in os.environ:
                    assert AZURE_IC_MODEL == "gpt-4o-mini"
                else:
                    assert AZURE_IC_MODEL == os.environ["AZURE_IC_MODEL"]

    def test_azure_ic_model_source_references_env_var(self):
        """Verify the source code reads from AZURE_IC_MODEL env var."""
        from src.agents import intent_classifier

        source = inspect.getsource(intent_classifier)
        assert 'os.environ.get("AZURE_IC_MODEL"' in source
        assert '"gpt-4o-mini"' in source


class TestResponseGeneratorAgent:
    """SPEC-1411: ResponseGeneratorAgent class in response_generator.py."""

    def test_class_exists(self):
        from src.agents.response_generator import ResponseGeneratorAgent

        assert ResponseGeneratorAgent is not None

    def test_inherits_from_base_agent(self):
        from src.agents.response_generator import ResponseGeneratorAgent
        from src.agents.base import AgentRedBaseAgent

        assert issubclass(ResponseGeneratorAgent, AgentRedBaseAgent)

    def test_can_be_instantiated(self):
        from src.agents.response_generator import ResponseGeneratorAgent

        agent = ResponseGeneratorAgent()
        assert agent is not None

    def test_has_process_method(self):
        from src.agents.response_generator import ResponseGeneratorAgent

        assert hasattr(ResponseGeneratorAgent, "process")
        assert callable(getattr(ResponseGeneratorAgent, "process"))


class TestResponseGeneratorStream:
    """SPEC-1414: response_generator.py has generate_stream method."""

    def test_generate_stream_method_exists(self):
        from src.agents.response_generator import ResponseGeneratorAgent

        assert hasattr(ResponseGeneratorAgent, "generate_stream")

    def test_generate_stream_is_async(self):
        from src.agents.response_generator import ResponseGeneratorAgent

        assert inspect.isasyncgenfunction(ResponseGeneratorAgent.generate_stream) or \
               inspect.iscoroutinefunction(ResponseGeneratorAgent.generate_stream)

    def test_generate_stream_signature(self):
        from src.agents.response_generator import ResponseGeneratorAgent

        sig = inspect.signature(ResponseGeneratorAgent.generate_stream)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "customer_message" in params
        assert "intent" in params
        assert "knowledge_context" in params
        assert "system_prompt" in params
