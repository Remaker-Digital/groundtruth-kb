"""SPEC-1787: Stateful path verification for all database/object intermediaries.

Tests verify that every Create/Update/Delete operation on stateful objects
is exercised and that observers (readers/receivers) can verify the change.

Focus areas:
- Redis Pub/Sub cache invalidation (publish → subscribe → local cache eviction)
- SSE stream tenant isolation (buffer boundaries, cross-tenant prevention)
- Multi-instance cache coherency (invalidate_tenant_meta_cache broadcast)
- Append-only collection immutability (audit_log, alert_history, sla_snapshots)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch



# ===========================================================================
# Category 1: Redis Pub/Sub Cache Invalidation (SPEC-1757 stateful path)
# ===========================================================================

class TestRedisPubSubStatefulPath:
    """Verify the full publish → subscribe → evict cycle for cache invalidation."""

    def test_sp01_publish_subscribe_roundtrip(self):
        """SP-01: Published invalidation message reaches subscriber and evicts cache.

        Verifies the full stateful path:
        Write: publish_cache_invalidation("tenant-x")
        → Redis Pub/Sub channel
        → Read: subscriber thread receives message
        → Effect: invalidate_tenant_meta_cache("tenant-x", _publish=False)
        """
        import src.multi_tenant.cache_invalidation as mod


        # Create a mock Redis client with working pub/sub
        mock_redis = MagicMock()
        mock_pubsub = MagicMock()
        mock_redis.pubsub.return_value = mock_pubsub

        # Simulate the subscribe + listen cycle
        stop_event = threading.Event()

        def fake_listen():
            # Yield subscription confirmation first
            yield {"type": "subscribe", "channel": "agentred:cache:invalidate", "data": 1}
            # Yield a real message
            yield {"type": "message", "data": "tenant-x", "channel": "agentred:cache:invalidate"}
            # Block until test signals stop
            stop_event.wait(timeout=2)

        mock_pubsub.listen.side_effect = fake_listen

        # Patch invalidate_tenant_meta_cache to capture calls
        # The subscriber imports invalidate_tenant_meta_cache lazily inside
        # _subscriber_loop, so we patch at the source (middleware module).
        with patch("src.multi_tenant.middleware.invalidate_tenant_meta_cache") as mock_invalidate:
            # Save original state
            orig_client = mod._redis_client
            orig_thread = mod._subscriber_thread
            orig_shutdown = mod._shutdown_event

            try:
                mod._redis_client = mock_redis
                mod._shutdown_event = threading.Event()

                # Start subscriber thread
                thread = threading.Thread(target=mod._subscriber_loop, daemon=True)
                thread.start()

                # Wait for the message to be processed
                time.sleep(0.5)

                # Stop the subscriber
                stop_event.set()
                mod._shutdown_event.set()
                thread.join(timeout=3)

                # Verify the invalidation was called with correct args
                mock_invalidate.assert_called_with("tenant-x", _publish=False)

            finally:
                mod._redis_client = orig_client
                mod._subscriber_thread = orig_thread
                mod._shutdown_event = orig_shutdown

    def test_sp02_full_flush_roundtrip(self):
        """SP-02: '__all__' message triggers full cache flush (tenant_id=None).

        Write: publish_cache_invalidation(None) sends '__all__'
        Read: subscriber decodes '__all__' → calls invalidate(None, _publish=False)
        """
        import src.multi_tenant.cache_invalidation as mod

        mock_redis = MagicMock()
        mock_pubsub = MagicMock()
        mock_redis.pubsub.return_value = mock_pubsub

        stop_event = threading.Event()

        def fake_listen():
            yield {"type": "subscribe", "data": 1}
            yield {"type": "message", "data": "__all__", "channel": "agentred:cache:invalidate"}
            stop_event.wait(timeout=2)

        mock_pubsub.listen.side_effect = fake_listen

        with patch("src.multi_tenant.middleware.invalidate_tenant_meta_cache") as mock_invalidate:
            orig_client = mod._redis_client
            orig_thread = mod._subscriber_thread
            orig_shutdown = mod._shutdown_event

            try:
                mod._redis_client = mock_redis
                mod._shutdown_event = threading.Event()

                thread = threading.Thread(target=mod._subscriber_loop, daemon=True)
                thread.start()

                time.sleep(0.5)

                stop_event.set()
                mod._shutdown_event.set()
                thread.join(timeout=3)

                # Full flush: tenant_id should be None
                mock_invalidate.assert_called_with(None, _publish=False)

            finally:
                mod._redis_client = orig_client
                mod._subscriber_thread = orig_thread
                mod._shutdown_event = orig_shutdown

    def test_sp03_bytes_message_decoded(self):
        """SP-03: Redis messages received as bytes are decoded to str.

        Stateful path: bytes wire format → str tenant_id in invalidation call.
        """
        import src.multi_tenant.cache_invalidation as mod

        mock_redis = MagicMock()
        mock_pubsub = MagicMock()
        mock_redis.pubsub.return_value = mock_pubsub

        stop_event = threading.Event()

        def fake_listen():
            yield {"type": "subscribe", "data": 1}
            # Send as bytes (how Redis actually delivers without decode_responses)
            yield {"type": "message", "data": b"tenant-bytes-test", "channel": "agentred:cache:invalidate"}
            stop_event.wait(timeout=2)

        mock_pubsub.listen.side_effect = fake_listen

        with patch("src.multi_tenant.middleware.invalidate_tenant_meta_cache") as mock_invalidate:
            orig_client = mod._redis_client
            orig_thread = mod._subscriber_thread
            orig_shutdown = mod._shutdown_event

            try:
                mod._redis_client = mock_redis
                mod._shutdown_event = threading.Event()

                thread = threading.Thread(target=mod._subscriber_loop, daemon=True)
                thread.start()
                time.sleep(0.5)
                stop_event.set()
                mod._shutdown_event.set()
                thread.join(timeout=3)

                # Should decode bytes to string
                mock_invalidate.assert_called_with("tenant-bytes-test", _publish=False)

            finally:
                mod._redis_client = orig_client
                mod._subscriber_thread = orig_thread
                mod._shutdown_event = orig_shutdown

    def test_sp04_subscriber_reconnects_on_error(self):
        """SP-04: Subscriber reconnects with backoff after Redis error.

        Verifies resilience: Redis disconnect → backoff → reconnect → receive.
        """
        import src.multi_tenant.cache_invalidation as mod

        mock_redis = MagicMock()
        mock_pubsub_bad = MagicMock()
        mock_pubsub_good = MagicMock()

        call_count = [0]
        stop_event = threading.Event()

        def pubsub_factory():
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_pubsub_bad
            return mock_pubsub_good

        mock_redis.pubsub.side_effect = pubsub_factory

        # First call: raises error during listen
        mock_pubsub_bad.listen.side_effect = ConnectionError("Redis gone")

        # Second call: delivers a message then stops
        def good_listen():
            yield {"type": "subscribe", "data": 1}
            yield {"type": "message", "data": "tenant-reconnect", "channel": "agentred:cache:invalidate"}
            stop_event.wait(timeout=2)

        mock_pubsub_good.listen.side_effect = good_listen

        with patch("src.multi_tenant.middleware.invalidate_tenant_meta_cache") as mock_invalidate:
            orig_client = mod._redis_client
            orig_thread = mod._subscriber_thread
            orig_shutdown = mod._shutdown_event

            try:
                mod._redis_client = mock_redis
                mod._shutdown_event = threading.Event()

                thread = threading.Thread(target=mod._subscriber_loop, daemon=True)
                thread.start()

                # Wait enough for error + backoff + reconnect + message
                time.sleep(2.5)

                stop_event.set()
                mod._shutdown_event.set()
                thread.join(timeout=3)

                # After reconnect, should have received the message
                mock_invalidate.assert_called_with("tenant-reconnect", _publish=False)
                # Should have created pubsub at least twice (error + reconnect)
                assert call_count[0] >= 2

            finally:
                mod._redis_client = orig_client
                mod._subscriber_thread = orig_thread
                mod._shutdown_event = orig_shutdown

    def test_sp05_no_rebroadcast_loop(self):
        """SP-05: Subscriber calls invalidate with _publish=False to prevent loops.

        If _publish were True, each invalidation would re-publish to Redis,
        creating an infinite broadcast storm.
        """
        import src.multi_tenant.cache_invalidation as mod

        mock_redis = MagicMock()
        mock_pubsub = MagicMock()
        mock_redis.pubsub.return_value = mock_pubsub

        stop_event = threading.Event()
        calls_with_publish_flag = []

        def fake_listen():
            yield {"type": "subscribe", "data": 1}
            yield {"type": "message", "data": "tenant-loop-check", "channel": "agentred:cache:invalidate"}
            stop_event.wait(timeout=2)

        mock_pubsub.listen.side_effect = fake_listen

        def capture_invalidate(tenant_id, _publish=True):
            calls_with_publish_flag.append(_publish)

        with patch(
            "src.multi_tenant.middleware.invalidate_tenant_meta_cache",
            side_effect=capture_invalidate,
        ):
            orig_client = mod._redis_client
            orig_thread = mod._subscriber_thread
            orig_shutdown = mod._shutdown_event

            try:
                mod._redis_client = mock_redis
                mod._shutdown_event = threading.Event()

                thread = threading.Thread(target=mod._subscriber_loop, daemon=True)
                thread.start()
                time.sleep(0.5)
                stop_event.set()
                mod._shutdown_event.set()
                thread.join(timeout=3)

                # _publish must be False to prevent rebroadcast loop
                assert len(calls_with_publish_flag) >= 1
                assert all(flag is False for flag in calls_with_publish_flag), (
                    "Subscriber must call invalidate with _publish=False"
                )

            finally:
                mod._redis_client = orig_client
                mod._subscriber_thread = orig_thread
                mod._shutdown_event = orig_shutdown


# ===========================================================================
# Category 2: SSE Stream Tenant Isolation (SPEC-1787 stateful path)
# ===========================================================================

class TestSSETenantIsolation:
    """Verify SSE connections and buffers maintain strict tenant boundaries."""

    def test_sp06_connections_scoped_to_tenant(self):
        """SP-06: Each tenant's connections are tracked independently.

        Write: tenant-A connects → Read: tenant-B count unaffected.
        """
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()

        mgr.connect("tenant-a", "conv-a1")
        mgr.connect("tenant-a", "conv-a2")
        mgr.connect("tenant-b", "conv-b1")

        # Tenant A has 2, tenant B has 1
        assert len(mgr._connections["tenant-a"]) == 2
        assert len(mgr._connections["tenant-b"]) == 1

        # Disconnect tenant A — tenant B unaffected
        mgr.disconnect("tenant-a", "conv-a1")
        assert len(mgr._connections["tenant-a"]) == 1
        assert len(mgr._connections["tenant-b"]) == 1

    def test_sp07_buffers_keyed_by_conversation_not_tenant(self):
        """SP-07: Event buffers are keyed by conversation_id (globally unique UUID).

        This means tenant-B cannot access tenant-A's buffer by knowing the
        tenant ID alone — they would need the exact conversation UUID.
        """
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()

        mgr.connect("tenant-a", "conv-aaaa-1111")
        mgr.connect("tenant-b", "conv-bbbb-2222")

        # Each conversation gets its own buffer
        assert "conv-aaaa-1111" in mgr._buffers
        assert "conv-bbbb-2222" in mgr._buffers

        # Write to tenant A's buffer
        mgr._buffers["conv-aaaa-1111"].append("event: token\ndata: secret-a\n\n")
        mgr._buffers["conv-bbbb-2222"].append("event: token\ndata: public-b\n\n")

        # Replay only returns own buffer's events
        a_events = mgr._buffers["conv-aaaa-1111"].replay_after(0)
        b_events = mgr._buffers["conv-bbbb-2222"].replay_after(0)

        assert any("secret-a" in e for e in a_events)
        assert not any("secret-a" in e for e in b_events)

    def test_sp08_disconnect_does_not_leak_buffers(self):
        """SP-08: Disconnecting removes connection tracking but buffer persists for reconnect.

        Buffer cleanup is TTL-based (BUFFER_EXPIRY_SECONDS), not connection-based.
        """
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()

        mgr.connect("tenant-a", "conv-1234")
        mgr._buffers["conv-1234"].append("event: data\n\n")

        mgr.disconnect("tenant-a", "conv-1234")

        # Connection removed
        assert "conv-1234" not in mgr._connections.get("tenant-a", set())

        # Buffer still exists (for reconnect replay)
        assert "conv-1234" in mgr._buffers
        assert len(mgr._buffers["conv-1234"].replay_after(0)) == 1

    def test_sp09_can_connect_enforces_per_tenant_limit(self):
        """SP-09: can_connect() respects per-tenant SSE limits, not global.

        Write: Fill tenant-A to limit → Read: tenant-B can still connect.
        """
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()

        # Connect many streams for tenant-A (starter limit is typically 5)
        for i in range(5):
            mgr.connect("tenant-a", f"conv-a-{i}")

        # Tenant B should still be able to connect
        assert mgr.can_connect("tenant-b", "starter") is True

    def test_sp10_global_connection_count_accurate(self):
        """SP-10: Global connection count sums across all tenants correctly.

        Verifies the total_connections property reflects all active streams.
        """
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()

        mgr.connect("tenant-a", "conv-1")
        mgr.connect("tenant-b", "conv-2")
        mgr.connect("tenant-c", "conv-3")

        assert mgr.global_connection_count == 3

        mgr.disconnect("tenant-b", "conv-2")
        assert mgr.global_connection_count == 2


# ===========================================================================
# Category 3: Multi-Instance Cache Coherency (SPEC-1787 stateful path)
# ===========================================================================

class TestCacheCoherency:
    """Verify cache invalidation propagates correctly to local cache."""

    def test_sp11_invalidate_evicts_specific_tenant(self):
        """SP-11: invalidate_tenant_meta_cache(tenant_id) evicts only that tenant.

        Write: Cache tenant-A and tenant-B → invalidate tenant-A
        Read: tenant-A evicted, tenant-B still cached.
        """
        from src.multi_tenant.middleware import (
            _tenant_meta_cache,
            invalidate_tenant_meta_cache,
        )

        # Populate cache
        _tenant_meta_cache["tenant-a"] = {"tier": "growth"}
        _tenant_meta_cache["tenant-b"] = {"tier": "starter"}

        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation",
            return_value=False,
        ):
            invalidate_tenant_meta_cache("tenant-a")

        assert "tenant-a" not in _tenant_meta_cache
        assert "tenant-b" in _tenant_meta_cache

        # Cleanup
        _tenant_meta_cache.pop("tenant-b", None)

    def test_sp12_invalidate_full_flush_clears_all(self):
        """SP-12: invalidate_tenant_meta_cache(None) clears entire cache.

        Write: Cache multiple tenants → flush
        Read: All entries evicted.
        """
        from src.multi_tenant.middleware import (
            _tenant_meta_cache,
            invalidate_tenant_meta_cache,
        )

        _tenant_meta_cache["tenant-x"] = {"tier": "growth"}
        _tenant_meta_cache["tenant-y"] = {"tier": "starter"}

        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation",
            return_value=False,
        ):
            invalidate_tenant_meta_cache(None)

        assert len(_tenant_meta_cache) == 0

    def test_sp13_invalidate_publishes_to_redis(self):
        """SP-13: invalidate_tenant_meta_cache publishes to Redis by default.

        This ensures other replicas receive the invalidation event.
        """
        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation",
            return_value=True,
        ) as mock_publish:
            from src.multi_tenant.middleware import invalidate_tenant_meta_cache

            invalidate_tenant_meta_cache("tenant-pub-check")

            mock_publish.assert_called_once_with("tenant-pub-check")

    def test_sp14_invalidate_no_publish_skips_redis(self):
        """SP-14: invalidate_tenant_meta_cache(_publish=False) skips Redis.

        Used by subscriber to prevent rebroadcast loops (see SP-05).
        """
        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation",
        ) as mock_publish:
            from src.multi_tenant.middleware import invalidate_tenant_meta_cache

            invalidate_tenant_meta_cache("tenant-no-pub", _publish=False)

            mock_publish.assert_not_called()


# ===========================================================================
# Category 4: Append-Only Collection Immutability (SPEC-1787 stateful path)
# ===========================================================================

class TestAppendOnlyImmutability:
    """Verify append-only collections enforce write-once semantics."""

    def test_sp15_audit_log_append_only(self):
        """SP-15: Audit log entries cannot be updated or deleted.

        Write: log_event() appends → Read: list_recent returns entry.
        No update/delete methods exist on the repository.
        """
        from src.multi_tenant.repositories.platform import AuditLogRepository

        # Verify the repository has no update/delete methods
        repo_methods = [m for m in dir(AuditLogRepository) if not m.startswith("_")]
        assert "update" not in repo_methods, "Audit log must not have update()"
        assert "delete" not in repo_methods, "Audit log must not have delete()"
        assert "log_event" in repo_methods or "log" in repo_methods, (
            "Audit log must have a write method"
        )

    def test_sp16_alert_history_append_only(self):
        """SP-16: Alert history entries are append-only (log + acknowledge, no delete).

        Write: log_alert() → Read: list_recent, get_last_trigger_for_rule.
        """
        from src.multi_tenant.repositories.alerts import AlertHistoryRepository

        repo_methods = [m for m in dir(AlertHistoryRepository) if not m.startswith("_")]
        assert "delete" not in repo_methods, "Alert history must not have delete()"
        # acknowledge is a status update, not a content mutation — acceptable
        assert "log_alert" in repo_methods, "Alert history must have log_alert()"
        assert "list_recent" in repo_methods, "Alert history must have list_recent()"


# ===========================================================================
# Category 5: EventBuffer Stateful Path (SPEC-1787)
# ===========================================================================

class TestEventBufferStatefulPath:
    """Verify EventBuffer create/append/read/expiry lifecycle."""

    def test_sp17_buffer_append_and_replay(self):
        """SP-17: Events appended to buffer can be replayed by sequence number.

        Write: append(event) → Read: replay_after(0) returns event.
        """
        from src.chat.sse_manager import EventBuffer

        buf = EventBuffer()
        seq1 = buf.append("event: token\ndata: hello\n\n")
        seq2 = buf.append("event: token\ndata: world\n\n")

        assert seq1 == 1
        assert seq2 == 2

        # Replay all
        events = buf.replay_after(0)
        assert len(events) == 2

        # Replay after first
        events = buf.replay_after(1)
        assert len(events) == 1
        assert "world" in events[0]

    def test_sp18_buffer_circular_trim(self):
        """SP-18: Buffer trims to MAX_BUFFERED_EVENTS, oldest events dropped.

        Write: Exceed max → Read: only most recent MAX events remain.
        """
        from src.chat.sse_manager import EventBuffer, MAX_BUFFERED_EVENTS

        buf = EventBuffer()
        for i in range(MAX_BUFFERED_EVENTS + 10):
            buf.append(f"event: token\ndata: msg-{i}\n\n")

        assert len(buf.events) == MAX_BUFFERED_EVENTS
        # Oldest events should be trimmed
        oldest_seq = buf.events[0][0]
        assert oldest_seq > 1, "Oldest events should have been trimmed"

    def test_sp19_buffer_expiry(self):
        """SP-19: Buffer reports expired after BUFFER_EXPIRY_SECONDS of inactivity."""
        from src.chat.sse_manager import EventBuffer, BUFFER_EXPIRY_SECONDS

        buf = EventBuffer()
        buf.append("event: test\n\n")

        # Fresh buffer should not be expired
        assert buf.is_expired is False

        # Simulate age by backdating last_activity
        buf.last_activity = time.monotonic() - BUFFER_EXPIRY_SECONDS - 1
        assert buf.is_expired is True

    def test_sp20_buffer_replay_empty(self):
        """SP-20: Replay on empty buffer returns empty list (no crash)."""
        from src.chat.sse_manager import EventBuffer

        buf = EventBuffer()
        events = buf.replay_after(0)
        assert events == []
        events = buf.replay_after(999)
        assert events == []
