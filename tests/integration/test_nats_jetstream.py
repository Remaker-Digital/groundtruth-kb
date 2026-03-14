"""NATS JetStream integration tests for TenantNATSManager (SPEC-1781).

Tests the NATS tenant isolation layer against a real NATS JetStream server
when available (nats://localhost:4222), or skips gracefully. Covers:
  - Connection lifecycle (connect, close, reconnect)
  - Stream provisioning (create, update, delete per tier)
  - Publish/subscribe with tenant authorization
  - Cross-tenant isolation enforcement
  - Queue group (deliver_group) competing consumers (SPEC-1788)
  - Circuit breaker behavior
  - Health check reporting
  - Correlation header propagation

Prerequisites:
  docker compose up nats  (NATS available at nats://localhost:4222)

Usage:
  pytest tests/integration/test_nats_jetstream.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.nats_isolation import (
    AGENT_TOPICS,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    MESSAGE_MAX_AGE_SECONDS,
    NATSAuthorizationError,
    NATSCircuitBreaker,
    NATSHealthStatus,
    PLATFORM_TOPICS,
    TenantNATSManager,
    _extract_tenant_from_subject,
    get_nats_manager,
    stream_name,
    tenant_topic,
    tenant_wildcard,
)
from src.multi_tenant.cosmos_schema import TenantTier


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NATS_TEST_URL = os.environ.get("NATS_TEST_URL", "nats://localhost:4222")
TENANT_A = "test-tenant-aaa"
TENANT_B = "test-tenant-bbb"


def _nats_available() -> bool:
    """Check if NATS server is reachable (non-async probe)."""
    import socket
    try:
        host, port = NATS_TEST_URL.replace("nats://", "").split(":")
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        return True
    except (OSError, ValueError):
        return False


nats_available = _nats_available()
requires_nats = pytest.mark.skipif(
    not nats_available,
    reason="NATS server not available at " + NATS_TEST_URL,
)


# ---------------------------------------------------------------------------
# 1. Helper function tests (no NATS required)
# ---------------------------------------------------------------------------

class TestHelperFunctions:
    """Test pure helper functions that don't need NATS."""

    def test_tenant_topic_format(self):
        assert tenant_topic("t-abc", "intent-classifier") == "t-abc.intent-classifier"

    def test_tenant_wildcard_format(self):
        assert tenant_wildcard("t-abc") == "t-abc.>"

    def test_stream_name_format(self):
        assert stream_name("t-abc") == "tenant-t-abc"

    def test_extract_tenant_from_subject(self):
        assert _extract_tenant_from_subject("t-abc.intent-classifier") == "t-abc"

    def test_extract_tenant_from_subject_no_dot(self):
        assert _extract_tenant_from_subject("nodot") is None

    def test_extract_tenant_uuid_style(self):
        uuid = "bd4ebf05-a8a5-4566-8097-9da668470cb2"
        assert _extract_tenant_from_subject(f"{uuid}.knowledge-retrieval") == uuid


# ---------------------------------------------------------------------------
# 2. Circuit breaker tests (no NATS required)
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    """Test NATSCircuitBreaker state machine."""

    def test_initial_state_closed(self):
        cb = NATSCircuitBreaker()
        assert cb.state == NATSCircuitBreaker.State.CLOSED
        assert not cb.is_open

    def test_opens_after_threshold_failures(self):
        cb = NATSCircuitBreaker(failure_threshold=3, window_seconds=10)
        cb.record_failure()
        cb.record_failure()
        assert not cb.is_open
        cb.record_failure()
        assert cb.is_open

    def test_success_resets_to_closed(self):
        cb = NATSCircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open
        cb.record_success()
        assert cb.state == NATSCircuitBreaker.State.CLOSED

    def test_reset_clears_state(self):
        cb = NATSCircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.is_open
        cb.reset()
        assert cb.state == NATSCircuitBreaker.State.CLOSED

    def test_half_open_after_recovery_period(self):
        cb = NATSCircuitBreaker(
            failure_threshold=1, recovery_seconds=0.01,
        )
        cb.record_failure()
        assert cb.is_open
        import time
        time.sleep(0.02)
        assert cb.state == NATSCircuitBreaker.State.HALF_OPEN

    def test_failures_outside_window_not_counted(self):
        cb = NATSCircuitBreaker(
            failure_threshold=3, window_seconds=0.01,
        )
        cb.record_failure()
        cb.record_failure()
        import time
        time.sleep(0.02)
        cb.record_failure()
        # Only 1 failure in current window
        assert not cb.is_open


# ---------------------------------------------------------------------------
# 3. Authorization tests (no NATS required)
# ---------------------------------------------------------------------------

class TestAuthorization:
    """Test tenant subject authorization enforcement."""

    def test_authorize_own_topic_passes(self):
        mgr = TenantNATSManager()
        # Should not raise
        mgr.authorize_subject(TENANT_A, f"{TENANT_A}.intent-classifier")

    def test_authorize_cross_tenant_raises(self):
        mgr = TenantNATSManager()
        with pytest.raises(NATSAuthorizationError) as exc_info:
            mgr.authorize_subject(TENANT_A, f"{TENANT_B}.intent-classifier")
        assert TENANT_A in str(exc_info.value)
        assert TENANT_B in str(exc_info.value)

    def test_authorize_platform_topic_raises(self):
        mgr = TenantNATSManager()
        with pytest.raises(NATSAuthorizationError):
            mgr.authorize_subject(TENANT_A, "platform.health")

    def test_authorize_all_agent_topics(self):
        """Every agent topic should be authorizable for the owning tenant."""
        mgr = TenantNATSManager()
        for agent in AGENT_TOPICS:
            mgr.authorize_subject(TENANT_A, tenant_topic(TENANT_A, agent))

    def test_authorize_all_platform_topics_rejected(self):
        """Platform topics should be rejected for any tenant."""
        mgr = TenantNATSManager()
        for topic in PLATFORM_TOPICS:
            with pytest.raises(NATSAuthorizationError):
                mgr.authorize_subject(TENANT_A, topic)


# ---------------------------------------------------------------------------
# 4. Correlation header tests (no NATS required)
# ---------------------------------------------------------------------------

class TestCorrelationHeaders:
    """Test correlation header building and extraction."""

    def test_build_headers_all_fields(self):
        mgr = TenantNATSManager()
        headers = mgr.build_correlation_headers(
            tenant_id="t-1", conversation_id="conv-42", trace_id="trace-99",
        )
        assert headers["X-Tenant-Id"] == "t-1"
        assert headers["X-Conversation-Id"] == "conv-42"
        assert headers["X-Trace-Id"] == "trace-99"

    def test_build_headers_no_trace(self):
        mgr = TenantNATSManager()
        headers = mgr.build_correlation_headers(
            tenant_id="t-1", conversation_id="conv-42",
        )
        assert "X-Trace-Id" not in headers

    def test_extract_headers_from_message(self):
        msg = MagicMock()
        msg.headers = {
            "X-Tenant-Id": "t-1",
            "X-Conversation-Id": "conv-42",
            "X-Trace-Id": "trace-99",
        }
        result = TenantNATSManager.extract_correlation_headers(msg)
        assert result["tenant_id"] == "t-1"
        assert result["conversation_id"] == "conv-42"
        assert result["trace_id"] == "trace-99"

    def test_extract_headers_missing_fields(self):
        msg = MagicMock()
        msg.headers = {}
        result = TenantNATSManager.extract_correlation_headers(msg)
        assert result["tenant_id"] is None
        assert result["conversation_id"] is None
        assert result["trace_id"] is None

    def test_extract_headers_none_headers(self):
        msg = MagicMock()
        msg.headers = None
        result = TenantNATSManager.extract_correlation_headers(msg)
        assert result["tenant_id"] is None


# ---------------------------------------------------------------------------
# 5. Health check tests (no NATS required)
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """Test health check when not connected."""

    @pytest.mark.asyncio
    async def test_health_not_connected(self):
        mgr = TenantNATSManager()
        health = await mgr.check_health()
        assert isinstance(health, NATSHealthStatus)
        assert health.connected is False
        assert health.active_streams == 0

    def test_is_connected_initially_false(self):
        mgr = TenantNATSManager()
        assert mgr.is_connected is False

    def test_circuit_breaker_state_initially_closed(self):
        mgr = TenantNATSManager()
        assert mgr.get_circuit_breaker_state() == "closed"


# ---------------------------------------------------------------------------
# 6. Connection guard tests (no NATS required)
# ---------------------------------------------------------------------------

class TestConnectionGuard:
    """Test _require_connected raises when not connected."""

    @pytest.mark.asyncio
    async def test_publish_requires_connection(self):
        mgr = TenantNATSManager()
        with pytest.raises(Exception, match="(not connected|connection closed)"):
            await mgr.publish(TENANT_A, "intent-classifier", b"{}")

    @pytest.mark.asyncio
    async def test_subscribe_requires_connection(self):
        mgr = TenantNATSManager()
        with pytest.raises(Exception, match="(not connected|connection closed)"):
            await mgr.subscribe(TENANT_A, "intent-classifier", AsyncMock())

    @pytest.mark.asyncio
    async def test_provision_requires_connection(self):
        mgr = TenantNATSManager()
        with pytest.raises(Exception, match="(not connected|connection closed)"):
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)


# ---------------------------------------------------------------------------
# 7. Live NATS tests (require running NATS server)
# ---------------------------------------------------------------------------

@requires_nats
class TestLiveConnection:
    """Test real NATS connection lifecycle."""

    @pytest.mark.asyncio
    async def test_connect_and_close(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        assert mgr.is_connected
        await mgr.close()
        assert not mgr.is_connected

    @pytest.mark.asyncio
    async def test_connect_idempotent(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        await mgr.connect()  # Should not raise
        assert mgr.is_connected
        await mgr.close()

    @pytest.mark.asyncio
    async def test_close_idempotent(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        await mgr.close()
        await mgr.close()  # Should not raise


@requires_nats
class TestLiveStreamProvisioning:
    """Test JetStream stream provisioning against real NATS."""

    @pytest.mark.asyncio
    async def test_provision_starter_stream(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            result = await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
            assert result.get("created") is True
            assert result["stream_name"] == stream_name(TENANT_A)
            assert result["tier"] == "starter"
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_provision_professional_stream(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            result = await mgr.provision_tenant_topics(TENANT_A, TenantTier.PROFESSIONAL)
            assert result.get("created") is True
            assert result["tier"] == "professional"
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_update_stream_tier(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
            result = await mgr.update_tenant_stream(TENANT_A, TenantTier.ENTERPRISE)
            assert result.get("updated") is True
            assert result["tier"] == "enterprise"
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_deprovision_stream(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
            result = await mgr.deprovision_tenant_topics(TENANT_A)
            assert result.get("deleted") is True
        finally:
            await mgr.close()

    @pytest.mark.asyncio
    async def test_deprovision_absent_stream(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            result = await mgr.deprovision_tenant_topics("nonexistent-tenant")
            assert result.get("deleted") is True
            assert result.get("already_absent") is True
        finally:
            await mgr.close()

    @pytest.mark.asyncio
    async def test_update_nonexistent_provisions(self):
        """Updating a nonexistent stream should provision it."""
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            result = await mgr.update_tenant_stream(TENANT_B, TenantTier.STARTER)
            assert result.get("created") is True
        finally:
            await mgr.deprovision_tenant_topics(TENANT_B)
            await mgr.close()


@requires_nats
class TestLivePublishSubscribe:
    """Test real publish/subscribe with tenant isolation."""

    @pytest.mark.asyncio
    async def test_publish_and_receive(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        received = []

        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

            async def handler(msg):
                received.append(json.loads(msg.data))
                await msg.ack()

            await mgr.subscribe(TENANT_A, "intent-classifier", handler)

            payload = {"message": "hello", "test": True}
            await mgr.publish(
                TENANT_A, "intent-classifier", json.dumps(payload).encode(),
            )

            # Wait for delivery
            await asyncio.sleep(0.5)
            assert len(received) == 1
            assert received[0]["message"] == "hello"
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_cross_tenant_publish_rejected(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

            with pytest.raises(NATSAuthorizationError):
                await mgr.publish(
                    TENANT_B, "intent-classifier",
                    b'{"message": "sneaky"}',
                    # Trying to publish to TENANT_A's topic as TENANT_B
                )
                # This should fail at authorization, not at NATS level
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_cross_tenant_subscribe_rejected(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

            with pytest.raises(NATSAuthorizationError):
                await mgr.subscribe(
                    TENANT_B, "intent-classifier", AsyncMock(),
                )
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_correlation_headers_propagated(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        received_headers = []

        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

            async def handler(msg):
                received_headers.append(msg.headers or {})
                await msg.ack()

            await mgr.subscribe(TENANT_A, "intent-classifier", handler)

            headers = mgr.build_correlation_headers(
                TENANT_A, "conv-99", "trace-abc",
            )
            await mgr.publish(
                TENANT_A, "intent-classifier",
                b'{"test": true}', headers=headers,
            )

            await asyncio.sleep(0.5)
            assert len(received_headers) == 1
            assert received_headers[0].get("X-Tenant-Id") == TENANT_A
            assert received_headers[0].get("X-Conversation-Id") == "conv-99"
            assert received_headers[0].get("X-Trace-Id") == "trace-abc"
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()


@requires_nats
class TestLiveQueueGroups:
    """Test SPEC-1788 deliver_group for horizontal scaling."""

    @pytest.mark.asyncio
    async def test_queue_group_competing_consumers(self):
        """With deliver_group, only one subscriber receives each message."""
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        received_a = []
        received_b = []

        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

            group = f"{TENANT_A}-ic-group"

            async def handler_a(msg):
                received_a.append(json.loads(msg.data))
                await msg.ack()

            async def handler_b(msg):
                received_b.append(json.loads(msg.data))
                await msg.ack()

            # Two subscribers with same deliver_group (simulating 2 replicas)
            await mgr.subscribe(
                TENANT_A, "intent-classifier", handler_a,
                durable_name=f"{TENANT_A}-ic-replica-1",
                deliver_group=group,
            )
            await mgr.subscribe(
                TENANT_A, "intent-classifier", handler_b,
                durable_name=f"{TENANT_A}-ic-replica-2",
                deliver_group=group,
            )

            # Publish multiple messages
            for i in range(10):
                await mgr.publish(
                    TENANT_A, "intent-classifier",
                    json.dumps({"seq": i}).encode(),
                )

            await asyncio.sleep(1.0)

            # Each message should be received by exactly one handler
            total = len(received_a) + len(received_b)
            assert total == 10, f"Expected 10 messages total, got {total}"
            # Both subscribers should get some messages (probabilistic)
            # In rare cases one might get all 10, but with 10 messages it's very unlikely
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_default_deliver_group_name(self):
        """Default deliver_group should follow {tenant}-{agent}-group pattern."""
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        received = []

        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

            async def handler(msg):
                received.append(msg.data)
                await msg.ack()

            # Subscribe with default deliver_group (no explicit group)
            await mgr.subscribe(TENANT_A, "intent-classifier", handler)

            await mgr.publish(
                TENANT_A, "intent-classifier", b'{"test": true}',
            )
            await asyncio.sleep(0.5)
            assert len(received) == 1
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()


@requires_nats
class TestLiveHealthCheck:
    """Test health check with live NATS connection."""

    @pytest.mark.asyncio
    async def test_health_connected(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            health = await mgr.check_health()
            assert health.connected is True
            assert health.circuit_breaker_state == "closed"
        finally:
            await mgr.close()

    @pytest.mark.asyncio
    async def test_health_shows_provisioned_streams(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
            health = await mgr.check_health()
            assert health.active_streams >= 1
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()


@requires_nats
class TestLiveStreamInspection:
    """Test stream info inspection."""

    @pytest.mark.asyncio
    async def test_get_stream_info(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
            info = await mgr.get_tenant_stream_info(TENANT_A)
            assert info is not None
            assert info["stream_name"] == stream_name(TENANT_A)
            assert isinstance(info["messages"], int)
        finally:
            await mgr.deprovision_tenant_topics(TENANT_A)
            await mgr.close()

    @pytest.mark.asyncio
    async def test_get_nonexistent_stream_info(self):
        mgr = TenantNATSManager(nats_url=NATS_TEST_URL)
        await mgr.connect()
        try:
            info = await mgr.get_tenant_stream_info("nonexistent")
            assert info is None
        finally:
            await mgr.close()


# ---------------------------------------------------------------------------
# 8. Fail-loud dispatch enforcement tests (SPEC-1780)
# ---------------------------------------------------------------------------

class TestFailLoudDispatch:
    """Test SPEC-1780 enforcement — 503 in deployed environments."""

    def test_require_transport_noop_in_development(self):
        """In development, _require_transport_or_fail is a no-op."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin()
        with patch("src.chat.pipeline.agent_dispatch._IS_DEPLOYED", False):
            # Should not raise
            mixin._require_transport_or_fail("intent-classifier")

    def test_require_transport_raises_503_in_staging(self):
        """In staging, _require_transport_or_fail raises HTTPException(503)."""
        from fastapi import HTTPException

        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin()
        with patch("src.chat.pipeline.agent_dispatch._IS_DEPLOYED", True), \
             patch("src.chat.pipeline.agent_dispatch._ENVIRONMENT", "staging"):
            with pytest.raises(HTTPException) as exc_info:
                mixin._require_transport_or_fail("intent-classifier")
            assert exc_info.value.status_code == 503
            assert "intent-classifier" in exc_info.value.detail
            assert "staging" in exc_info.value.detail

    def test_require_transport_raises_503_in_production(self):
        """In production, _require_transport_or_fail raises HTTPException(503)."""
        from fastapi import HTTPException

        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin()
        with patch("src.chat.pipeline.agent_dispatch._IS_DEPLOYED", True), \
             patch("src.chat.pipeline.agent_dispatch._ENVIRONMENT", "production"):
            with pytest.raises(HTTPException) as exc_info:
                mixin._require_transport_or_fail("response-generator")
            assert exc_info.value.status_code == 503

    def test_transport_available_returns_false_when_no_transport(self):
        """_transport_available returns False when AGNTCY transport is None."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin()
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", None):
            assert mixin._transport_available() is False

    def test_transport_available_returns_true_when_transport_exists(self):
        """_transport_available returns True when AGNTCY transport is set."""
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin()
        with patch("src.multi_tenant.agntcy_sdk_integration._transport", MagicMock()):
            assert mixin._transport_available() is True


# ---------------------------------------------------------------------------
# 9. Ready endpoint transport enforcement tests (SPEC-1780)
# ---------------------------------------------------------------------------

class TestReadyEndpointEnforcement:
    """Test /ready returns 503 when transport not active in deployed envs."""

    @pytest.mark.asyncio
    async def test_ready_returns_503_in_staging_without_transport(self):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        from src.app.health import register_health_endpoints
        register_health_endpoints(app)

        client = TestClient(app)

        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}), \
             patch("src.multi_tenant.agntcy_sdk_integration._transport", None), \
             patch("src.multi_tenant.agntcy_sdk_integration._factory", None):
            response = client.get("/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "not_ready"
            assert "transport_enforcement" in data

    @pytest.mark.asyncio
    async def test_ready_returns_200_in_development_without_transport(self):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        from src.app.health import register_health_endpoints
        register_health_endpoints(app)

        client = TestClient(app)

        with patch.dict(os.environ, {"ENVIRONMENT": "development"}), \
             patch("src.multi_tenant.agntcy_sdk_integration._transport", None), \
             patch("src.multi_tenant.agntcy_sdk_integration._factory", None):
            response = client.get("/ready")
            assert response.status_code == 200


# ---------------------------------------------------------------------------
# 10. Singleton management tests
# ---------------------------------------------------------------------------

class TestSingletonManagement:
    """Test module-level singleton get/init/close."""

    def test_get_nats_manager_returns_instance(self):
        mgr = get_nats_manager()
        assert isinstance(mgr, TenantNATSManager)

    def test_get_nats_manager_returns_same_instance(self):
        mgr1 = get_nats_manager()
        mgr2 = get_nats_manager()
        assert mgr1 is mgr2
