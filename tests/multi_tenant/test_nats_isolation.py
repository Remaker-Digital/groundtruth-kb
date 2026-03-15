"""NATS tenant isolation tests — P1 pre-launch (§5.1).

Test IDs: NI-01 through NI-25.

Validates:
    - Topic namespace format ({tenant_id}.{agent})
    - All 6 agent topics per tenant
    - JetStream stream provisioning and deprovisioning lifecycle
    - Tier change handling (queue depth adjustment)
    - Cross-tenant authorization enforcement
    - Correlation header propagation
    - NATSCircuitBreaker state machine (3 failures/10s, 5s recovery)
    - Health check, lifecycle, graceful degradation
    - Stream configuration (WorkQueue retention, tier-aware queue depth)
    - Singleton pattern

Module under test: src/multi_tenant/nats_isolation.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
from src.multi_tenant.nats_isolation import (
    AGENT_TOPICS,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_RECOVERY_SECONDS,
    CIRCUIT_BREAKER_WINDOW_SECONDS,
    DEFAULT_RETENTION,
    MAX_MSG_SIZE,
    MESSAGE_MAX_AGE_SECONDS,
    NATSAuthorizationError,
    NATSCircuitBreaker,
    NATSHealthStatus,
    PLATFORM_TOPICS,
    STREAM_PREFIX,
    TenantNATSManager,
    _extract_tenant_from_subject,
    close_nats_manager,
    get_nats_manager,
    init_nats_manager,
    stream_name,
    tenant_topic,
    tenant_wildcard,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_A = "t-alpha-001"
TENANT_B = "t-beta-002"


@pytest.fixture
def manager() -> TenantNATSManager:
    """Create a TenantNATSManager with a mock NATS connection.

    The mock JetStream context supports add_stream, update_stream,
    delete_stream, purge_stream, stream_info, find_stream_name_by_subject,
    streams_info, subscribe, and publish — all as AsyncMock.
    """
    mgr = TenantNATSManager(nats_url="nats://mock:4222")

    # Simulate a connected state by injecting mock client + JetStream
    mock_nc = MagicMock()
    mock_nc.is_connected = True
    mock_nc.is_closed = False
    mock_nc.client_id = "mock-client-1"
    mock_nc.drain = AsyncMock()
    mock_nc.close = AsyncMock()

    mock_js = MagicMock()
    mock_js.add_stream = AsyncMock(return_value=MagicMock())
    mock_js.update_stream = AsyncMock(return_value=MagicMock())
    mock_js.delete_stream = AsyncMock()
    mock_js.purge_stream = AsyncMock()
    mock_js.publish = AsyncMock(
        return_value=MagicMock(stream="tenant-t-alpha-001", seq=1),
    )
    mock_js.subscribe = AsyncMock(return_value=MagicMock(unsubscribe=AsyncMock()))
    mock_js.find_stream_name_by_subject = AsyncMock(return_value="tenant-t-alpha-001")
    mock_js.streams_info = AsyncMock(return_value=[])

    # Build a mock StreamInfo for stream_info calls
    mock_stream_config = MagicMock()
    mock_stream_config.max_msgs_per_subject = 5
    mock_stream_info = MagicMock()
    mock_stream_info.config = mock_stream_config
    mock_js.stream_info = AsyncMock(return_value=mock_stream_info)

    mgr._nc = mock_nc
    mgr._js = mock_js

    return mgr


@pytest.fixture
def breaker() -> NATSCircuitBreaker:
    """Create a fresh NATSCircuitBreaker with default thresholds."""
    return NATSCircuitBreaker()


# ===========================================================================
# NI-01: Topic namespace format
# ===========================================================================


class TestTopicNamespace:
    """NI-01 through NI-02, NI-23, NI-24: Topic naming validation."""

    def test_ni_01_topic_format(self) -> None:
        """NI-01: tenant_topic produces {tenant_id}.{agent}."""
        result = tenant_topic(TENANT_A, "intent-classifier")
        assert result == f"{TENANT_A}.intent-classifier"

    def test_ni_02_all_six_agent_topics(self) -> None:
        """NI-02: All 6 agent topics are defined and form valid subjects."""
        assert len(AGENT_TOPICS) == 6
        expected = {
            "intent-classifier",
            "knowledge-retrieval",
            "response-generator",
            "escalation-handler",
            "analytics-collector",
            "critic-supervisor",
        }
        assert set(AGENT_TOPICS) == expected

        # Each produces a valid tenant-scoped subject
        for agent in AGENT_TOPICS:
            subject = tenant_topic(TENANT_A, agent)
            assert subject.startswith(TENANT_A)
            assert subject.endswith(agent)

    def test_ni_23_stream_name_format(self) -> None:
        """NI-23: Stream name follows tenant-{tenant_id} format."""
        assert stream_name(TENANT_A) == f"tenant-{TENANT_A}"
        assert stream_name("t-xyz").startswith(STREAM_PREFIX)

    def test_ni_24_wildcard_subject(self) -> None:
        """NI-24: Wildcard subject is {tenant_id}.> for all sub-subjects."""
        wc = tenant_wildcard(TENANT_A)
        assert wc == f"{TENANT_A}.>"


# ===========================================================================
# NI-03 to NI-05: Provisioning lifecycle
# ===========================================================================


class TestProvisioning:
    """NI-03, NI-04, NI-05, NI-18, NI-19, NI-22: Stream lifecycle."""

    @pytest.mark.asyncio
    async def test_ni_03_provision_creates_stream(self, manager: TenantNATSManager) -> None:
        """NI-03: provision_tenant_topics creates a JetStream stream."""
        result = await manager.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

        assert result["created"] is True
        assert result["stream_name"] == stream_name(TENANT_A)
        assert result["tier"] == "starter"
        manager._js.add_stream.assert_awaited_once()

        # Verify the StreamConfig was built with correct subjects
        call_args = manager._js.add_stream.call_args
        config = call_args[0][0]  # First positional arg
        assert config.name == stream_name(TENANT_A)
        assert tenant_wildcard(TENANT_A) in config.subjects

    @pytest.mark.asyncio
    async def test_ni_04_deprovision_purges_and_deletes(self, manager: TenantNATSManager) -> None:
        """NI-04: deprovision_tenant_topics purges messages, then deletes stream."""
        # Provision first to track the stream
        await manager.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

        result = await manager.deprovision_tenant_topics(TENANT_A)

        assert result["deleted"] is True
        assert result["tenant_id"] == TENANT_A
        manager._js.purge_stream.assert_awaited_once_with(stream_name(TENANT_A))
        manager._js.delete_stream.assert_awaited_once_with(stream_name(TENANT_A))

    @pytest.mark.asyncio
    async def test_ni_04_deprovision_absent_stream(self, manager: TenantNATSManager) -> None:
        """NI-04 supplement: deprovisioning an absent stream returns success."""
        from nats.js.errors import NotFoundError as JetStreamNotFoundError

        manager._js.purge_stream = AsyncMock(
            side_effect=JetStreamNotFoundError(),
        )
        result = await manager.deprovision_tenant_topics(TENANT_A)
        assert result["deleted"] is True
        assert result.get("already_absent") is True

    @pytest.mark.asyncio
    async def test_ni_05_update_stream_tier_change(self, manager: TenantNATSManager) -> None:
        """NI-05: update_tenant_stream adjusts queue depth on tier change."""
        result = await manager.update_tenant_stream(TENANT_A, TenantTier.ENTERPRISE)

        assert result["updated"] is True
        assert result["tier"] == "enterprise"
        # queue_depth removed from TIER_DEFAULTS; product code falls back to 5
        expected_depth = TIER_DEFAULTS.get("enterprise", {}).get("queue_depth", 5)
        assert result["max_msgs_per_subject"] == expected_depth
        manager._js.update_stream.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ni_05_update_missing_stream_provisions(self, manager: TenantNATSManager) -> None:
        """NI-05 supplement: updating a missing stream provisions it instead."""
        from nats.js.errors import NotFoundError as JetStreamNotFoundError

        manager._js.find_stream_name_by_subject = AsyncMock(
            side_effect=JetStreamNotFoundError(),
        )
        result = await manager.update_tenant_stream(TENANT_A, TenantTier.PROFESSIONAL)

        # Should fall through to provision
        assert result.get("created") is True
        manager._js.add_stream.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ni_18_workqueue_retention(self, manager: TenantNATSManager) -> None:
        """NI-18: Provisioned streams use WorkQueue retention policy."""
        await manager.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

        call_args = manager._js.add_stream.call_args
        config = call_args[0][0]
        assert config.retention == DEFAULT_RETENTION

    @pytest.mark.asyncio
    async def test_ni_19_tier_aware_queue_depth(self, manager: TenantNATSManager) -> None:
        """NI-19: Queue depth uses fallback default (queue_depth removed from TIER_DEFAULTS)."""
        for tier in [TenantTier.STARTER, TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE]:
            manager._js.add_stream.reset_mock()
            result = await manager.provision_tenant_topics(TENANT_A, tier)

            # queue_depth removed from TIER_DEFAULTS; product code falls back to 5
            expected_depth = TIER_DEFAULTS.get(tier.value, {}).get("queue_depth", 5)
            assert result["max_msgs_per_subject"] == expected_depth

            call_args = manager._js.add_stream.call_args
            config = call_args[0][0]
            assert config.max_msgs_per_subject == expected_depth

    @pytest.mark.asyncio
    async def test_ni_19_trial_tier_queue_depth(self, manager: TenantNATSManager) -> None:
        """NI-19 supplement: Trial tier uses fallback queue depth."""
        result = await manager.provision_tenant_topics(TENANT_A, TenantTier.TRIAL)
        # queue_depth removed from TIER_DEFAULTS; product code falls back to 5
        expected_depth = TIER_DEFAULTS.get("trial", {}).get("queue_depth", 5)
        assert result["max_msgs_per_subject"] == expected_depth

    @pytest.mark.asyncio
    async def test_ni_22_independent_streams(self, manager: TenantNATSManager) -> None:
        """NI-22: Multiple tenants get independent JetStream streams."""
        result_a = await manager.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
        result_b = await manager.provision_tenant_topics(TENANT_B, TenantTier.PROFESSIONAL)

        assert result_a["stream_name"] != result_b["stream_name"]
        assert result_a["stream_name"] == stream_name(TENANT_A)
        assert result_b["stream_name"] == stream_name(TENANT_B)
        assert manager._js.add_stream.await_count == 2


# ===========================================================================
# NI-06 to NI-09: Authorization enforcement
# ===========================================================================


class TestAuthorization:
    """NI-06 through NI-09: Cross-tenant access prevention."""

    def test_ni_06_authorize_own_subject(self, manager: TenantNATSManager) -> None:
        """NI-06: authorize_subject allows tenant to access own namespace."""
        # Should not raise
        subject = tenant_topic(TENANT_A, "intent-classifier")
        manager.authorize_subject(TENANT_A, subject)

    def test_ni_07_reject_cross_tenant_access(self, manager: TenantNATSManager) -> None:
        """NI-07: authorize_subject rejects access to another tenant's topic."""
        subject = tenant_topic(TENANT_B, "response-generator")
        with pytest.raises(NATSAuthorizationError) as exc_info:
            manager.authorize_subject(TENANT_A, subject)

        assert exc_info.value.tenant_id == TENANT_A
        assert exc_info.value.subject == subject

    def test_ni_07_reject_platform_topics(self, manager: TenantNATSManager) -> None:
        """NI-07 supplement: Tenants cannot access platform-wide topics."""
        for platform_topic in PLATFORM_TOPICS:
            with pytest.raises(NATSAuthorizationError):
                manager.authorize_subject(TENANT_A, platform_topic)

    @pytest.mark.asyncio
    async def test_ni_08_cross_tenant_publish_blocked(self, manager: TenantNATSManager) -> None:
        """NI-08: NATSAuthorizationError raised on cross-tenant publish.

        publish() builds subject from tenant_id + agent, so the public API
        structurally prevents cross-tenant subjects. We verify that the
        authorization layer (which publish delegates to) correctly rejects
        subjects belonging to another tenant.
        """
        # Verify the authorization layer rejects cross-tenant subjects
        with pytest.raises(NATSAuthorizationError):
            manager.authorize_subject(TENANT_A, f"{TENANT_B}.intent-classifier")

        # Also verify that publish() does call authorize_subject internally
        # by checking a valid publish goes through authorization
        with patch.object(manager, "authorize_subject", side_effect=NATSAuthorizationError(TENANT_A, "spoofed")):
            with pytest.raises(NATSAuthorizationError):
                await manager.publish(TENANT_A, "intent-classifier", b'{"test": true}')

    @pytest.mark.asyncio
    async def test_ni_09_cross_tenant_subscribe_blocked(self, manager: TenantNATSManager) -> None:
        """NI-09: NATSAuthorizationError raised on cross-tenant subscribe."""
        # subscribe() builds subject from tenant_id + agent, so it cannot
        # produce a cross-tenant subject. Verify the authorization layer
        # directly.
        with pytest.raises(NATSAuthorizationError):
            manager.authorize_subject(TENANT_A, f"{TENANT_B}.response-generator")

    def test_ni_06_extract_tenant_from_subject(self) -> None:
        """NI-06 supplement: _extract_tenant_from_subject parses correctly."""
        assert _extract_tenant_from_subject(f"{TENANT_A}.intent-classifier") == TENANT_A
        assert _extract_tenant_from_subject("no-dot-subject") is None
        assert _extract_tenant_from_subject("") is None

    @pytest.mark.asyncio
    async def test_ni_21_subscribe_tenant_filtered(self, manager: TenantNATSManager) -> None:
        """NI-21: subscribe() creates subscription scoped to tenant's stream."""
        callback = AsyncMock()
        sub = await manager.subscribe(TENANT_A, "intent-classifier", callback)

        # Verify subscribe was called with the correct tenant-scoped subject
        manager._js.subscribe.assert_awaited_once()
        call_kwargs = manager._js.subscribe.call_args
        assert call_kwargs[0][0] == tenant_topic(TENANT_A, "intent-classifier")
        assert call_kwargs[1]["stream"] == stream_name(TENANT_A)

        # Subscription tracked
        assert "intent-classifier" in manager._subscriptions.get(TENANT_A, {})


# ===========================================================================
# NI-10 to NI-11: Correlation headers
# ===========================================================================


class TestCorrelationHeaders:
    """NI-10 and NI-11: Correlation ID propagation via NATS headers."""

    def test_ni_10_build_correlation_headers(self, manager: TenantNATSManager) -> None:
        """NI-10: build_correlation_headers populates required NATS headers."""
        headers = manager.build_correlation_headers(
            tenant_id=TENANT_A,
            conversation_id="conv-123",
            trace_id="trace-abc",
        )
        assert headers["X-Tenant-Id"] == TENANT_A
        assert headers["X-Conversation-Id"] == "conv-123"
        assert headers["X-Trace-Id"] == "trace-abc"

    def test_ni_10_build_headers_no_trace(self, manager: TenantNATSManager) -> None:
        """NI-10 supplement: trace_id is optional."""
        headers = manager.build_correlation_headers(
            tenant_id=TENANT_A,
            conversation_id="conv-456",
        )
        assert "X-Tenant-Id" in headers
        assert "X-Conversation-Id" in headers
        assert "X-Trace-Id" not in headers

    def test_ni_11_extract_correlation_headers(self) -> None:
        """NI-11: extract_correlation_headers reads NATS message headers."""
        mock_msg = MagicMock()
        mock_msg.headers = {
            "X-Tenant-Id": TENANT_A,
            "X-Conversation-Id": "conv-789",
            "X-Trace-Id": "trace-def",
        }
        result = TenantNATSManager.extract_correlation_headers(mock_msg)
        assert result["tenant_id"] == TENANT_A
        assert result["conversation_id"] == "conv-789"
        assert result["trace_id"] == "trace-def"

    def test_ni_11_extract_missing_headers(self) -> None:
        """NI-11 supplement: Missing headers return None values."""
        mock_msg = MagicMock()
        mock_msg.headers = {}
        result = TenantNATSManager.extract_correlation_headers(mock_msg)
        assert result["tenant_id"] is None
        assert result["conversation_id"] is None
        assert result["trace_id"] is None

    def test_ni_11_extract_null_headers(self) -> None:
        """NI-11 supplement: Message with no headers dict returns None values."""
        mock_msg = MagicMock()
        mock_msg.headers = None
        result = TenantNATSManager.extract_correlation_headers(mock_msg)
        assert result["tenant_id"] is None


# ===========================================================================
# NI-12 to NI-13: Circuit breaker
# ===========================================================================


class TestCircuitBreaker:
    """NI-12 and NI-13: NATSCircuitBreaker state machine."""

    def test_ni_12_starts_closed(self, breaker: NATSCircuitBreaker) -> None:
        """NI-12 prerequisite: breaker starts in CLOSED state."""
        assert breaker.state == NATSCircuitBreaker.State.CLOSED
        assert not breaker.is_open

    def test_ni_12_three_failures_open(self, breaker: NATSCircuitBreaker) -> None:
        """NI-12: 3 failures within window → OPEN."""
        assert breaker._failure_threshold == CIRCUIT_BREAKER_FAILURE_THRESHOLD
        assert breaker._window_seconds == CIRCUIT_BREAKER_WINDOW_SECONDS

        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            breaker.record_failure()

        assert breaker.state == NATSCircuitBreaker.State.OPEN
        assert breaker.is_open

    def test_ni_12_fewer_failures_stay_closed(self, breaker: NATSCircuitBreaker) -> None:
        """NI-12 supplement: Fewer than threshold failures keeps CLOSED."""
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD - 1):
            breaker.record_failure()

        assert breaker.state == NATSCircuitBreaker.State.CLOSED

    def test_ni_13_recovery_to_half_open(self, breaker: NATSCircuitBreaker) -> None:
        """NI-13: After recovery_seconds, OPEN transitions to HALF_OPEN."""
        # Trip the breaker
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            breaker.record_failure()
        assert breaker.state == NATSCircuitBreaker.State.OPEN

        # Simulate passage of recovery time
        breaker._opened_at = time.monotonic() - CIRCUIT_BREAKER_RECOVERY_SECONDS - 1
        assert breaker.state == NATSCircuitBreaker.State.HALF_OPEN

    def test_ni_13_half_open_success_closes(self, breaker: NATSCircuitBreaker) -> None:
        """NI-13 supplement: Success in HALF_OPEN → CLOSED."""
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            breaker.record_failure()
        breaker._opened_at = time.monotonic() - CIRCUIT_BREAKER_RECOVERY_SECONDS - 1

        # Verify HALF_OPEN
        assert breaker.state == NATSCircuitBreaker.State.HALF_OPEN

        breaker.record_success()
        assert breaker.state == NATSCircuitBreaker.State.CLOSED

    def test_ni_13_half_open_failure_reopens(self, breaker: NATSCircuitBreaker) -> None:
        """NI-13 supplement: Failure in HALF_OPEN → OPEN again."""
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            breaker.record_failure()
        breaker._opened_at = time.monotonic() - CIRCUIT_BREAKER_RECOVERY_SECONDS - 1
        assert breaker.state == NATSCircuitBreaker.State.HALF_OPEN

        breaker.record_failure()
        assert breaker.state == NATSCircuitBreaker.State.OPEN

    def test_ni_12_reset_clears_state(self, breaker: NATSCircuitBreaker) -> None:
        """NI-12 supplement: reset() returns to CLOSED regardless of state."""
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            breaker.record_failure()
        assert breaker.is_open

        breaker.reset()
        assert breaker.state == NATSCircuitBreaker.State.CLOSED
        assert not breaker.is_open


# ===========================================================================
# NI-14: Health check
# ===========================================================================


class TestHealthCheck:
    """NI-14: Health check returns connection status."""

    @pytest.mark.asyncio
    async def test_ni_14_health_connected(self, manager: TenantNATSManager) -> None:
        """NI-14: Health check reports connected status."""
        health = await manager.check_health()

        assert isinstance(health, NATSHealthStatus)
        assert health.connected is True
        assert health.circuit_breaker_state == "closed"
        assert health.server_url == "nats://mock:4222"
        assert health.last_check_at  # Non-empty ISO timestamp

    @pytest.mark.asyncio
    async def test_ni_14_health_disconnected(self) -> None:
        """NI-14 supplement: Health check reports disconnected status."""
        mgr = TenantNATSManager(nats_url="nats://mock:4222")
        # No connection established — _nc is None
        health = await mgr.check_health()

        assert health.connected is False
        assert health.active_streams == 0
        assert "not_connected" in health.details.get("error", "")


# ===========================================================================
# NI-15 to NI-17: Lifecycle
# ===========================================================================


class TestLifecycle:
    """NI-15, NI-16, NI-17: Connection lifecycle and graceful degradation."""

    @pytest.mark.asyncio
    async def test_ni_15_init_establishes_connection(self) -> None:
        """NI-15: init_nats_manager establishes connection."""
        import src.multi_tenant.nats_isolation as mod

        # Save original singleton
        original = mod._manager

        try:
            mod._manager = None

            with patch.object(mod, "nats") as mock_nats_lib:
                mock_nc = AsyncMock()
                mock_nc.is_connected = True
                mock_nc.jetstream = MagicMock(return_value=MagicMock())
                mock_nats_lib.connect = AsyncMock(return_value=mock_nc)

                result = await init_nats_manager(nats_url="nats://test:4222")

                assert result is not None
                assert result.is_connected
                mock_nats_lib.connect.assert_awaited_once()
        finally:
            # Restore original singleton
            mod._manager = original

    @pytest.mark.asyncio
    async def test_ni_16_close_drains_and_closes(self, manager: TenantNATSManager) -> None:
        """NI-16: close() drains subscriptions and closes connection."""
        import src.multi_tenant.nats_isolation as mod

        # Capture reference to mock_nc before close() sets _nc = None
        mock_nc = manager._nc

        original = mod._manager
        try:
            mod._manager = manager
            await close_nats_manager()

            mock_nc.drain.assert_awaited_once()
            assert mod._manager is None
        finally:
            mod._manager = original

    @pytest.mark.asyncio
    async def test_ni_17_non_fatal_startup(self) -> None:
        """NI-17: NATS connection failure at startup is non-fatal."""
        mgr = TenantNATSManager(nats_url="nats://nonexistent:4222")

        with patch("src.multi_tenant.nats_isolation.nats") as mock_nats_lib:
            mock_nats_lib.connect = AsyncMock(
                side_effect=ConnectionRefusedError("Connection refused"),
            )
            with pytest.raises(ConnectionRefusedError):
                await mgr.connect()

        # Manager should not be connected but should still be usable
        # for health checks and state queries
        assert not mgr.is_connected


# ===========================================================================
# NI-20: Publish with circuit breaker protection
# ===========================================================================


class TestPublishResilience:
    """NI-20: Publish operations respect circuit breaker state."""

    @pytest.mark.asyncio
    async def test_ni_20_publish_blocked_when_open(self, manager: TenantNATSManager) -> None:
        """NI-20: publish() raises ConnectionClosedError when circuit breaker is OPEN."""
        from nats.errors import ConnectionClosedError

        # Trip the circuit breaker
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            manager._circuit_breaker.record_failure()
        assert manager._circuit_breaker.is_open

        with pytest.raises(ConnectionClosedError):
            await manager.publish(
                tenant_id=TENANT_A,
                agent="intent-classifier",
                data=b'{"test": true}',
            )

        # Verify the JetStream publish was never called (blocked before reaching it)
        manager._js.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ni_20_publish_success_records(self, manager: TenantNATSManager) -> None:
        """NI-20 supplement: Successful publish records success on breaker."""
        await manager.publish(
            tenant_id=TENANT_A,
            agent="intent-classifier",
            data=b'{"test": true}',
        )

        manager._js.publish.assert_awaited_once()
        # Breaker should still be closed
        assert manager._circuit_breaker.state == NATSCircuitBreaker.State.CLOSED

    @pytest.mark.asyncio
    async def test_ni_20_provision_blocked_when_open(self, manager: TenantNATSManager) -> None:
        """NI-20 supplement: provision returns error when breaker is OPEN."""
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            manager._circuit_breaker.record_failure()

        result = await manager.provision_tenant_topics(TENANT_A, TenantTier.STARTER)
        assert "error" in result
        assert result["error"] == "nats_circuit_breaker_open"


# ===========================================================================
# NI-25: Singleton pattern
# ===========================================================================


class TestSingleton:
    """NI-25: get_nats_manager returns same instance."""

    def test_ni_25_singleton(self) -> None:
        """NI-25: get_nats_manager() returns consistent singleton."""
        import src.multi_tenant.nats_isolation as mod

        original = mod._manager
        try:
            mod._manager = None
            mgr1 = get_nats_manager()
            mgr2 = get_nats_manager()
            assert mgr1 is mgr2
        finally:
            mod._manager = original

    def test_ni_25_reset_circuit_breaker(self, manager: TenantNATSManager) -> None:
        """NI-25 supplement: reset_circuit_breaker accessible via singleton."""
        for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            manager._circuit_breaker.record_failure()
        assert manager._circuit_breaker.is_open

        manager.reset_circuit_breaker()
        assert manager.get_circuit_breaker_state() == "closed"


# ===========================================================================
# NI supplement: Require-connected guard
# ===========================================================================


class TestRequireConnected:
    """Supplement: _require_connected guard on operations."""

    @pytest.mark.asyncio
    async def test_publish_requires_connection(self) -> None:
        """Publish raises ConnectionClosedError when not connected."""
        from nats.errors import ConnectionClosedError

        mgr = TenantNATSManager()
        with pytest.raises(ConnectionClosedError):
            await mgr.publish(TENANT_A, "intent-classifier", b"data")

    @pytest.mark.asyncio
    async def test_subscribe_requires_connection(self) -> None:
        """Subscribe raises ConnectionClosedError when not connected."""
        from nats.errors import ConnectionClosedError

        mgr = TenantNATSManager()
        with pytest.raises(ConnectionClosedError):
            await mgr.subscribe(TENANT_A, "intent-classifier", AsyncMock())

    @pytest.mark.asyncio
    async def test_provision_requires_connection(self) -> None:
        """Provision raises ConnectionClosedError when not connected."""
        from nats.errors import ConnectionClosedError

        mgr = TenantNATSManager()
        with pytest.raises(ConnectionClosedError):
            await mgr.provision_tenant_topics(TENANT_A, TenantTier.STARTER)

    @pytest.mark.asyncio
    async def test_deprovision_requires_connection(self) -> None:
        """Deprovision raises ConnectionClosedError when not connected."""
        from nats.errors import ConnectionClosedError

        mgr = TenantNATSManager()
        with pytest.raises(ConnectionClosedError):
            await mgr.deprovision_tenant_topics(TENANT_A)
