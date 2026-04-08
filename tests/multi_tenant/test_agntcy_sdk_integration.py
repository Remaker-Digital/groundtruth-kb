"""AGNTCY SDK integration tests — Phase 1 platform adoption.

Test IDs: ASDK-01 through ASDK-25.

Validates:
    - AgntcyFactory singleton creation and lifecycle
    - AgentTopic enum values match AgentRole and NATS topics
    - Transport creation (SLIM and NATS fallback)
    - A2A client creation via factory
    - MCP client creation via factory
    - SDK status introspection
    - Lifecycle management (init/close)
    - Environment variable configuration
    - Error handling (missing transport, missing endpoint)

Module under test: src/multi_tenant/agntcy_sdk_integration.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.multi_tenant.agntcy_sdk_integration import (
    AgentTopic,
    close_agntcy_sdk,
    create_a2a_client,
    create_mcp_client,
    get_agntcy_factory,
    get_default_transport,
    get_sdk_status,
    init_agntcy_sdk,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_singletons() -> None:
    """Reset module-level singletons between tests."""
    import src.multi_tenant.agntcy_sdk_integration as mod
    mod._factory = None
    mod._transport = None


@pytest.fixture(autouse=True)
def _clean_singletons():
    """Ensure each test starts with fresh singletons."""
    _reset_singletons()
    yield
    _reset_singletons()


# ---------------------------------------------------------------------------
# ASDK-01: AgentTopic enum values
# ---------------------------------------------------------------------------

class TestAgentTopicEnum:
    """ASDK-01 through ASDK-03: AgentTopic enum consistency."""

    def test_asdk_01_seven_agent_topics_defined(self) -> None:
        """ASDK-01: Exactly 7 agent topics are defined (6 AGNTCY + Co-pilot)."""
        assert len(AgentTopic) == 7

    def test_asdk_02_topic_values_match_agntcy_convention(self) -> None:
        """ASDK-02: Topic values use hyphenated lowercase (AGNTCY convention)."""
        expected = {
            "intent-classifier",
            "knowledge-retrieval",
            "response-generator",
            "escalation-handler",
            "analytics-collector",
            "critic-supervisor",
            "co-pilot",
        }
        actual = {t.value for t in AgentTopic}
        assert actual == expected

    def test_asdk_03_topic_values_match_agent_role(self) -> None:
        """ASDK-03: AgentTopic values match AgentRole enum in system_prompt_builder."""
        from src.multi_tenant.system_prompt_builder import AgentRole

        # Both enums should have the same string values
        agent_role_values = {r.value for r in AgentRole}
        agent_topic_values = {t.value for t in AgentTopic}
        assert agent_topic_values == agent_role_values, (
            f"AgentTopic and AgentRole values diverged: "
            f"topic_only={agent_topic_values - agent_role_values}, "
            f"role_only={agent_role_values - agent_topic_values}"
        )

    def test_asdk_04_topic_values_match_nats_agent_topics(self) -> None:
        """ASDK-04: NATS AGENT_TOPICS matches AgentTopic enum values."""
        from src.multi_tenant.nats_isolation import AGENT_TOPICS

        agent_topic_values = {t.value for t in AgentTopic}
        nats_topics = set(AGENT_TOPICS)
        # Since SPEC-1852, AGENT_TOPICS is registry-driven and includes all
        # core agents (including co-pilot). Both sets should match exactly.
        assert nats_topics == agent_topic_values, (
            f"NATS topics and AgentTopic enum diverged: "
            f"nats_only={nats_topics - agent_topic_values}, "
            f"enum_only={agent_topic_values - nats_topics}"
        )


# ---------------------------------------------------------------------------
# ASDK-05: Factory singleton
# ---------------------------------------------------------------------------

class TestAgntcyFactory:
    """ASDK-05 through ASDK-08: Factory singleton behavior."""

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_05_factory_singleton_created_once(self, mock_cls: MagicMock) -> None:
        """ASDK-05: get_agntcy_factory() creates exactly one instance."""
        mock_instance = MagicMock()
        mock_instance.registered_protocols.return_value = ["A2A", "MCP"]
        mock_instance.registered_transports.return_value = ["SLIM", "NATS"]
        mock_cls.return_value = mock_instance

        f1 = get_agntcy_factory()
        f2 = get_agntcy_factory()
        assert f1 is f2
        mock_cls.assert_called_once()

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_06_factory_passes_name(self, mock_cls: MagicMock) -> None:
        """ASDK-06: Factory is initialized with 'AgentRedFactory' name."""
        mock_instance = MagicMock()
        mock_instance.registered_protocols.return_value = []
        mock_instance.registered_transports.return_value = []
        mock_cls.return_value = mock_instance

        get_agntcy_factory()
        mock_cls.assert_called_once_with(
            name="AgentRedFactory",
            enable_tracing=False,
            log_level="INFO",
        )

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_07_factory_respects_tracing_env(self, mock_cls: MagicMock) -> None:
        """ASDK-07: AGNTCY_ENABLE_TRACING env var enables SDK tracing."""
        mock_instance = MagicMock()
        mock_instance.registered_protocols.return_value = []
        mock_instance.registered_transports.return_value = []
        mock_cls.return_value = mock_instance

        import src.multi_tenant.agntcy_sdk_integration as mod
        original = mod.ENABLE_SDK_TRACING
        try:
            mod.ENABLE_SDK_TRACING = True
            get_agntcy_factory()
            _, kwargs = mock_cls.call_args
            assert kwargs["enable_tracing"] is True
        finally:
            mod.ENABLE_SDK_TRACING = original

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_08_factory_exposes_protocols_and_transports(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-08: Factory reports available protocols and transports."""
        mock_instance = MagicMock()
        mock_instance.registered_protocols.return_value = ["A2A", "MCP"]
        mock_instance.registered_transports.return_value = ["SLIM", "NATS", "StreamableHTTP"]
        mock_cls.return_value = mock_instance

        factory = get_agntcy_factory()
        assert "A2A" in factory.registered_protocols()
        assert "MCP" in factory.registered_protocols()
        assert "SLIM" in factory.registered_transports()
        assert "NATS" in factory.registered_transports()


# ---------------------------------------------------------------------------
# ASDK-09: Transport creation
# ---------------------------------------------------------------------------

class TestTransportCreation:
    """ASDK-09 through ASDK-13: Transport creation and selection."""

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_09_slim_transport_preferred_when_configured(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-09: SLIM transport is created when SLIM endpoint is set."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig_type = mod.TRANSPORT_TYPE
        orig_endpoint = mod.SLIM_ENDPOINT
        try:
            mod.TRANSPORT_TYPE = "slim"
            mod.SLIM_ENDPOINT = "http://localhost:46357"
            transport = get_default_transport()
            assert transport is mock_transport
            mock_factory.create_transport.assert_called_once()
            call_kwargs = mock_factory.create_transport.call_args
            assert call_kwargs[1]["transport"] == "SLIM" or call_kwargs[0][0] == "SLIM"
        finally:
            mod.TRANSPORT_TYPE = orig_type
            mod.SLIM_ENDPOINT = orig_endpoint

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_10_nats_fallback_when_slim_not_configured(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-10: NATS transport is used when SLIM endpoint is empty."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig_type = mod.TRANSPORT_TYPE
        orig_endpoint = mod.SLIM_ENDPOINT
        orig_nats = mod.NATS_ENDPOINT
        try:
            mod.TRANSPORT_TYPE = "slim"
            mod.SLIM_ENDPOINT = ""
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            transport = get_default_transport()
            assert transport is mock_transport
            call_args = mock_factory.create_transport.call_args
            # Should fall through to NATS
            assert "NATS" in str(call_args)
        finally:
            mod.TRANSPORT_TYPE = orig_type
            mod.SLIM_ENDPOINT = orig_endpoint
            mod.NATS_ENDPOINT = orig_nats

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_11_no_transport_when_no_endpoint(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-11: Returns None when no transport endpoint is configured."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig_type = mod.TRANSPORT_TYPE
        orig_slim = mod.SLIM_ENDPOINT
        orig_nats = mod.NATS_ENDPOINT
        try:
            mod.TRANSPORT_TYPE = "slim"
            mod.SLIM_ENDPOINT = ""
            mod.NATS_ENDPOINT = ""
            transport = get_default_transport()
            assert transport is None
        finally:
            mod.TRANSPORT_TYPE = orig_type
            mod.SLIM_ENDPOINT = orig_slim
            mod.NATS_ENDPOINT = orig_nats

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_12_transport_singleton(self, mock_cls: MagicMock) -> None:
        """ASDK-12: get_default_transport() returns same instance on repeated calls."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig = mod.NATS_ENDPOINT
        try:
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            t1 = get_default_transport()
            t2 = get_default_transport()
            assert t1 is t2
            # Factory's create_transport should only be called once
            assert mock_factory.create_transport.call_count == 1
        finally:
            mod.NATS_ENDPOINT = orig

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_13_nats_transport_explicit_selection(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-13: AGNTCY_TRANSPORT_TYPE=nats directly selects NATS."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig_type = mod.TRANSPORT_TYPE
        orig_slim = mod.SLIM_ENDPOINT
        orig_nats = mod.NATS_ENDPOINT
        try:
            mod.TRANSPORT_TYPE = "nats"
            mod.SLIM_ENDPOINT = ""
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            transport = get_default_transport()
            assert transport is mock_transport
        finally:
            mod.TRANSPORT_TYPE = orig_type
            mod.SLIM_ENDPOINT = orig_slim
            mod.NATS_ENDPOINT = orig_nats


# ---------------------------------------------------------------------------
# ASDK-14: Client creation
# ---------------------------------------------------------------------------

class TestClientCreation:
    """ASDK-14 through ASDK-18: A2A and MCP client creation."""

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_14_a2a_client_creation_with_enum(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-14: create_a2a_client() works with AgentTopic enum."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_client = MagicMock()
        mock_factory.create_client.return_value = mock_client
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig = mod.NATS_ENDPOINT
        try:
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            client = create_a2a_client(AgentTopic.INTENT_CLASSIFIER)
            assert client is mock_client
            mock_factory.create_client.assert_called_once_with(
                "A2A",
                agent_topic="intent-classifier",
                transport=mock_transport,
            )
        finally:
            mod.NATS_ENDPOINT = orig

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_15_a2a_client_creation_with_string(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-15: create_a2a_client() works with raw string topic."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_client = MagicMock()
        mock_factory.create_client.return_value = mock_client
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig = mod.NATS_ENDPOINT
        try:
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            create_a2a_client("custom-agent")
            mock_factory.create_client.assert_called_once_with(
                "A2A",
                agent_topic="custom-agent",
                transport=mock_transport,
            )
        finally:
            mod.NATS_ENDPOINT = orig

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_16_a2a_client_fails_without_transport(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-16: create_a2a_client() raises RuntimeError when no transport."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig_slim = mod.SLIM_ENDPOINT
        orig_nats = mod.NATS_ENDPOINT
        try:
            mod.SLIM_ENDPOINT = ""
            mod.NATS_ENDPOINT = ""
            with pytest.raises(RuntimeError, match="no transport available"):
                create_a2a_client(AgentTopic.RESPONSE_GENERATOR)
        finally:
            mod.SLIM_ENDPOINT = orig_slim
            mod.NATS_ENDPOINT = orig_nats

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_17_mcp_client_creation(self, mock_cls: MagicMock) -> None:
        """ASDK-17: create_mcp_client() creates MCP protocol client."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_client = MagicMock()
        mock_factory.create_client.return_value = mock_client
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig = mod.NATS_ENDPOINT
        try:
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            client = create_mcp_client("external-tool-server")
            assert client is mock_client
            mock_factory.create_client.assert_called_once_with(
                "MCP",
                agent_topic="external-tool-server",
                transport=mock_transport,
            )
        finally:
            mod.NATS_ENDPOINT = orig

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_18_mcp_client_fails_without_transport_or_url(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-18: create_mcp_client() raises RuntimeError when no transport or server_url."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig_slim = mod.SLIM_ENDPOINT
        orig_nats = mod.NATS_ENDPOINT
        try:
            mod.SLIM_ENDPOINT = ""
            mod.NATS_ENDPOINT = ""
            with pytest.raises(RuntimeError, match="no transport or"):
                create_mcp_client("some-server")
        finally:
            mod.SLIM_ENDPOINT = orig_slim
            mod.NATS_ENDPOINT = orig_nats


# ---------------------------------------------------------------------------
# ASDK-19: SDK status introspection
# ---------------------------------------------------------------------------

class TestSDKStatus:
    """ASDK-19 through ASDK-21: Status reporting."""

    def test_asdk_19_status_before_init(self) -> None:
        """ASDK-19: get_sdk_status() returns uninitialized state before init."""
        status = get_sdk_status()
        assert status["sdk_initialized"] is False
        assert status["transport_active"] is False
        assert isinstance(status["agent_topics"], list)
        assert len(status["agent_topics"]) == 7

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_20_status_after_factory_init(self, mock_cls: MagicMock) -> None:
        """ASDK-20: Status shows initialized after factory creation."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = ["A2A", "MCP"]
        mock_factory.registered_transports.return_value = ["SLIM", "NATS"]
        mock_cls.return_value = mock_factory

        get_agntcy_factory()
        status = get_sdk_status()
        assert status["sdk_initialized"] is True
        assert "A2A" in status["available_protocols"]
        assert "MCP" in status["available_protocols"]

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    def test_asdk_21_status_includes_agent_topics(self, mock_cls: MagicMock) -> None:
        """ASDK-21: Status lists all 7 agent topics."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_cls.return_value = mock_factory

        get_agntcy_factory()
        status = get_sdk_status()
        assert "intent-classifier" in status["agent_topics"]
        assert "critic-supervisor" in status["agent_topics"]
        assert "co-pilot" in status["agent_topics"]
        assert len(status["agent_topics"]) == 7


# ---------------------------------------------------------------------------
# ASDK-22: Lifecycle management
# ---------------------------------------------------------------------------

class TestLifecycle:
    """ASDK-22 through ASDK-25: Init and close lifecycle."""

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    @pytest.mark.asyncio
    async def test_asdk_22_init_creates_factory(self, mock_cls: MagicMock) -> None:
        """ASDK-22: init_agntcy_sdk() creates factory singleton."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = ["A2A"]
        mock_factory.registered_transports.return_value = ["SLIM"]
        mock_cls.return_value = mock_factory

        await init_agntcy_sdk()

        import src.multi_tenant.agntcy_sdk_integration as mod
        assert mod._factory is not None

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    @pytest.mark.asyncio
    async def test_asdk_23_close_resets_singletons(self, mock_cls: MagicMock) -> None:
        """ASDK-23: close_agntcy_sdk() resets factory and transport."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_cls.return_value = mock_factory

        get_agntcy_factory()  # Initialize
        await close_agntcy_sdk()

        import src.multi_tenant.agntcy_sdk_integration as mod
        assert mod._factory is None
        assert mod._transport is None

    @patch("src.multi_tenant.agntcy_sdk_integration.AgntcyFactory")
    @pytest.mark.asyncio
    async def test_asdk_24_close_calls_transport_close(
        self, mock_cls: MagicMock
    ) -> None:
        """ASDK-24: close_agntcy_sdk() closes the transport."""
        mock_factory = MagicMock()
        mock_factory.registered_protocols.return_value = []
        mock_factory.registered_transports.return_value = []
        mock_transport = MagicMock()
        mock_factory.create_transport.return_value = mock_transport
        mock_cls.return_value = mock_factory

        import src.multi_tenant.agntcy_sdk_integration as mod
        orig = mod.NATS_ENDPOINT
        try:
            mod.NATS_ENDPOINT = "nats://localhost:4222"
            get_default_transport()  # Create transport
            await close_agntcy_sdk()
            mock_transport.close.assert_called_once()
        finally:
            mod.NATS_ENDPOINT = orig

    @pytest.mark.asyncio
    async def test_asdk_25_close_idempotent(self) -> None:
        """ASDK-25: close_agntcy_sdk() is safe to call when not initialized."""
        # Should not raise
        await close_agntcy_sdk()
        await close_agntcy_sdk()
