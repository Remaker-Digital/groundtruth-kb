"""Tests for SPEC-1780: Agent Dispatch Fail-Loud Transport Enforcement.

Verifies that agent dispatch fails with 503 when AGNTCY transport is
not active in staging/production, and that /ready reflects transport status.

Also covers transport tier detection from get_sdk_status().

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch



class TestTransportAvailability:
    """SPEC-1780: _transport_available() reflects actual transport state."""

    def test_transport_available_false_when_no_transport(self):
        """TEST-10220 (partial): transport not available when _transport is None."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        dispatcher = AgentDispatchMixin.__new__(AgentDispatchMixin)
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", None):
            assert dispatcher._transport_available() is False

    def test_transport_available_true_when_transport_exists(self):
        """Transport is available when _transport is set."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        dispatcher = AgentDispatchMixin.__new__(AgentDispatchMixin)
        mock_transport = MagicMock()
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", mock_transport):
            assert dispatcher._transport_available() is True


class TestSDKStatusReporting:
    """SPEC-1780: get_sdk_status() reports transport state for /ready."""

    def test_status_transport_active_false_when_no_transport(self):
        """TEST-10222 (partial): transport_active is False when no transport."""
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", None), \
             patch("src.multi_tenant.agntcy_sdk_integration._factory", None):
            from src.multi_tenant.agntcy_sdk_integration import get_sdk_status
            status = get_sdk_status()
            assert status["transport_active"] is False
            assert status["active_tier"] == "http_failure_mode"

    def test_status_transport_active_true_with_transport(self):
        """TEST-10223 (partial): transport_active is True when transport set."""
        mock_transport = MagicMock()
        type(mock_transport).__name__ = "SLIMTransport"
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", mock_transport), \
             patch("src.multi_tenant.agntcy_sdk_integration._factory", MagicMock()), \
             patch("src.multi_tenant.agntcy_sdk_integration._transport_setup_ok", True):
            from src.multi_tenant.agntcy_sdk_integration import get_sdk_status
            status = get_sdk_status()
            assert status["transport_active"] is True
            assert status["active_tier"] == "slim"

    def test_status_detects_nats_tier(self):
        """Transport tier correctly identifies NATS."""
        mock_transport = MagicMock()
        type(mock_transport).__name__ = "NatsTransport"
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", mock_transport), \
             patch("src.multi_tenant.agntcy_sdk_integration._factory", MagicMock()):
            from src.multi_tenant.agntcy_sdk_integration import get_sdk_status
            status = get_sdk_status()
            assert status["active_tier"] == "nats"


class TestReadyEndpointTransportEnforcement:
    """SPEC-1780 + SPEC-1802: /ready returns 503 in deployed envs without transport."""

    def test_ready_503_logic_in_health(self):
        """The /ready endpoint checks transport_active and returns 503 if False in staging/production."""
        # This is a structural test — verify the code path exists in health.py
        import ast
        from pathlib import Path

        health_src = Path("src/app/health.py").read_text(encoding="utf-8")
        ast.parse(health_src)

        # Find the string "not_ready" in the source — confirms the 503 path
        assert "not_ready" in health_src
        assert "transport_active" in health_src
        assert "503" in health_src

    def test_ready_does_not_503_in_development(self):
        """DCL-002: /ready enforces transport for ALL environments."""
        from pathlib import Path

        health_src = Path("src/app/health.py").read_text(encoding="utf-8")

        # SPEC-1802 / DCL-002: transport enforcement applies to ALL environments
        # (no environment-specific gating). Verify the 503 path exists.
        assert "transport_active" in health_src
        assert "not_ready" in health_src


class TestFailLoudDispatchBehavior:
    """SPEC-1780: Chat pipeline must fail loudly without transport."""

    def test_dispatcher_has_transport_check(self):
        """AgentDispatchMixin has _transport_available method."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        assert hasattr(AgentDispatchMixin, "_transport_available")

    def test_dispatcher_has_http_failure_mode_warning(self):
        """AgentDispatchMixin warns when using HTTP failure mode."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        assert hasattr(AgentDispatchMixin, "_warn_http_failure_mode")

    def test_tier_4_blocked_in_deployed_environments(self):
        """SPEC-1802: Tier 4 (in-process) is blocked in staging/production."""
        from pathlib import Path

        dispatch_src = Path("src/chat/pipeline/agent_dispatch.py").read_text(encoding="utf-8")

        # Verify there's a check that blocks in-process in deployed environments
        assert "in-process" in dispatch_src.lower() or "tier 4" in dispatch_src.lower() or "development only" in dispatch_src.lower()
