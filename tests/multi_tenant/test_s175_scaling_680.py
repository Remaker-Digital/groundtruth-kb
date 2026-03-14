"""Tests for S175 — 680-tenant scaling implementations.

Covers SPEC-1754 (Redis rate limit bridge), SPEC-1755 (Uvicorn workers),
SPEC-1756 (Global SSE limit), SPEC-1757 (Cache invalidation pub/sub),
SPEC-1758 (Pre-auth tracker LRU), SPEC-1759 (TOCTOU lock LRU),
SPEC-1760 (Health metrics endpoint).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import os
import threading
import time
from collections import OrderedDict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# =========================================================================
# SPEC-1754 — Redis Rate Limit Bridge
# =========================================================================

class TestRedisRateLimitBridge:
    """SPEC-1754: RateLimitMiddleware uses Redis when available."""

    def test_middleware_detects_redis_backend(self):
        """Middleware sets _use_redis=True when shared backend is Redis."""
        from src.multi_tenant.security_hardening import RedisRateLimitBackend

        mock_client = MagicMock()
        mock_client.pipeline.return_value = MagicMock()
        backend = RedisRateLimitBackend(mock_client, key_prefix="test:")

        with patch("src.multi_tenant.security_hardening.get_rate_limit_backend", return_value=backend):
            from src.multi_tenant.middleware import RateLimitMiddleware

            mw = RateLimitMiddleware(app=MagicMock())
            assert mw._use_redis is True

    def test_middleware_detects_inmemory_backend(self):
        """Middleware sets _use_redis=False when backend is in-memory."""
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend

        backend = InMemoryRateLimitBackend()

        with patch("src.multi_tenant.security_hardening.get_rate_limit_backend", return_value=backend):
            from src.multi_tenant.middleware import RateLimitMiddleware

            mw = RateLimitMiddleware(app=MagicMock())
            assert mw._use_redis is False

    def test_check_redis_returns_tuple_on_success(self):
        """_check_redis returns (allowed, remaining) tuple."""
        from src.multi_tenant.security_hardening import RedisRateLimitBackend

        mock_client = MagicMock()
        backend = RedisRateLimitBackend(mock_client, key_prefix="test:")
        backend.is_limited = MagicMock(return_value=False)

        with patch("src.multi_tenant.security_hardening.get_rate_limit_backend", return_value=backend):
            from src.multi_tenant.middleware import RateLimitMiddleware

            mw = RateLimitMiddleware(app=MagicMock())
            result = mw._check_redis("tenant-1", 500)
            assert result is not None
            allowed, remaining = result
            assert allowed is True
            assert remaining >= 0

    def test_check_redis_returns_none_on_failure(self):
        """_check_redis returns None on Redis error (fallback signal)."""
        from src.multi_tenant.security_hardening import RedisRateLimitBackend

        mock_client = MagicMock()
        backend = RedisRateLimitBackend(mock_client, key_prefix="test:")
        backend.is_limited = MagicMock(side_effect=Exception("Redis down"))

        with patch("src.multi_tenant.security_hardening.get_rate_limit_backend", return_value=backend):
            from src.multi_tenant.middleware import RateLimitMiddleware

            mw = RateLimitMiddleware(app=MagicMock())
            result = mw._check_redis("tenant-1", 500)
            assert result is None  # Signals fallback to local shards

    def test_check_redis_limited_returns_false_allowed(self):
        """_check_redis returns (False, 0) when rate limited."""
        from src.multi_tenant.security_hardening import RedisRateLimitBackend

        mock_client = MagicMock()
        backend = RedisRateLimitBackend(mock_client, key_prefix="test:")
        backend.is_limited = MagicMock(return_value=True)

        with patch("src.multi_tenant.security_hardening.get_rate_limit_backend", return_value=backend):
            from src.multi_tenant.middleware import RateLimitMiddleware

            mw = RateLimitMiddleware(app=MagicMock())
            result = mw._check_redis("tenant-1", 500)
            assert result is not None
            allowed, remaining = result
            assert allowed is False


# =========================================================================
# SPEC-1755 — Uvicorn Workers
# =========================================================================

class TestUvicornWorkers:
    """SPEC-1755: Dockerfile runs 4 Uvicorn workers."""

    def test_dockerfile_has_four_workers(self):
        """Dockerfile CMD specifies --workers 4."""
        dockerfile = open("Dockerfile").read()
        assert '--workers", "4"' in dockerfile or "--workers 4" in dockerfile


# =========================================================================
# SPEC-1756 — Global SSE Connection Limit
# =========================================================================

class TestGlobalSSELimit:
    """SPEC-1756: Global SSE connection cap across all tenants."""

    def test_global_max_connections_default(self):
        """GLOBAL_SSE_MAX_CONNECTIONS defaults to 5000."""
        from src.chat.sse_manager import GLOBAL_SSE_MAX_CONNECTIONS

        assert GLOBAL_SSE_MAX_CONNECTIONS == 5000

    def test_global_max_configurable_via_env(self):
        """GLOBAL_SSE_MAX_CONNECTIONS reads from SSE_MAX_CONNECTIONS env."""
        import importlib

        with patch.dict(os.environ, {"SSE_MAX_CONNECTIONS": "3000"}):
            import src.chat.sse_manager as mod
            importlib.reload(mod)
            assert mod.GLOBAL_SSE_MAX_CONNECTIONS == 3000
            # Restore
            os.environ.pop("SSE_MAX_CONNECTIONS", None)
            importlib.reload(mod)

    def test_can_connect_respects_global_limit(self):
        """can_connect returns False when global limit reached."""
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()
        # Simulate connections at global limit
        original = mgr.global_connection_count
        with patch.object(
            type(mgr), "global_connection_count",
            new_callable=lambda: property(lambda self: 5000),
        ):
            assert mgr.can_connect("tenant-1", "starter") is False

    def test_can_connect_allows_under_limit(self):
        """can_connect allows when under global limit."""
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()
        # Fresh manager has 0 connections
        assert mgr.can_connect("tenant-1", "starter") is True

    def test_global_connection_count_sums_all_tenants(self):
        """global_connection_count sums connections across all tenants."""
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()
        mgr._connections = {
            "t1": {"conn-1", "conn-2"},
            "t2": {"conn-3"},
        }
        assert mgr.global_connection_count == 3

    def test_is_global_limit_reached_property(self):
        """is_global_limit_reached is True when at or over limit."""
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()
        assert mgr.is_global_limit_reached is False

    def test_health_summary_includes_global_metrics(self):
        """health_summary() includes global SSE metrics."""
        from src.chat.sse_manager import SSEConnectionManager

        mgr = SSEConnectionManager()
        summary = mgr.health_summary()
        assert "global_connection_limit" in summary
        assert "global_limit_reached" in summary


# =========================================================================
# SPEC-1757 — Cross-Replica Cache Invalidation
# =========================================================================

class TestCacheInvalidation:
    """SPEC-1757: Redis pub/sub cache invalidation across replicas."""

    def test_publish_returns_false_without_redis(self):
        """publish_cache_invalidation returns False when Redis not configured."""
        from src.multi_tenant.cache_invalidation import publish_cache_invalidation

        # Module default state — no Redis
        import src.multi_tenant.cache_invalidation as mod

        original = mod._redis_client
        mod._redis_client = None
        try:
            assert publish_cache_invalidation("tenant-1") is False
        finally:
            mod._redis_client = original

    def test_publish_returns_true_with_redis(self):
        """publish_cache_invalidation publishes and returns True."""
        import src.multi_tenant.cache_invalidation as mod

        mock_client = MagicMock()
        original = mod._redis_client
        mod._redis_client = mock_client
        try:
            assert mod.publish_cache_invalidation("tenant-1") is True
            mock_client.publish.assert_called_once_with(
                "agentred:cache:invalidate", "tenant-1"
            )
        finally:
            mod._redis_client = original

    def test_publish_full_flush_sends_all_marker(self):
        """publish_cache_invalidation(None) sends '__all__' message."""
        import src.multi_tenant.cache_invalidation as mod

        mock_client = MagicMock()
        original = mod._redis_client
        mod._redis_client = mock_client
        try:
            mod.publish_cache_invalidation(None)
            mock_client.publish.assert_called_once_with(
                "agentred:cache:invalidate", "__all__"
            )
        finally:
            mod._redis_client = original

    def test_publish_handles_redis_error_gracefully(self):
        """publish_cache_invalidation returns False on Redis error."""
        import src.multi_tenant.cache_invalidation as mod

        mock_client = MagicMock()
        mock_client.publish.side_effect = Exception("Connection lost")
        original = mod._redis_client
        mod._redis_client = mock_client
        try:
            assert mod.publish_cache_invalidation("tenant-1") is False
        finally:
            mod._redis_client = original

    def test_invalidation_channel_name(self):
        """INVALIDATION_CHANNEL uses expected channel name."""
        from src.multi_tenant.cache_invalidation import INVALIDATION_CHANNEL

        assert INVALIDATION_CHANNEL == "agentred:cache:invalidate"

    def test_is_configured_false_by_default(self):
        """is_configured() returns False when no Redis client."""
        import src.multi_tenant.cache_invalidation as mod

        original_client = mod._redis_client
        original_thread = mod._subscriber_thread
        mod._redis_client = None
        mod._subscriber_thread = None
        try:
            assert mod.is_configured() is False
        finally:
            mod._redis_client = original_client
            mod._subscriber_thread = original_thread

    def test_is_configured_true_with_client_and_thread(self):
        """is_configured() returns True when both client and thread set."""
        import src.multi_tenant.cache_invalidation as mod

        original_client = mod._redis_client
        original_thread = mod._subscriber_thread
        mod._redis_client = MagicMock()
        mod._subscriber_thread = MagicMock()
        try:
            assert mod.is_configured() is True
        finally:
            mod._redis_client = original_client
            mod._subscriber_thread = original_thread

    def test_invalidate_tenant_meta_cache_publishes(self):
        """invalidate_tenant_meta_cache publishes to Redis."""
        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation"
        ) as mock_pub:
            from src.multi_tenant.middleware import invalidate_tenant_meta_cache

            invalidate_tenant_meta_cache("tenant-1")
            mock_pub.assert_called_once_with("tenant-1")

    def test_invalidate_tenant_meta_cache_no_publish_flag(self):
        """invalidate_tenant_meta_cache with _publish=False skips Redis."""
        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation"
        ) as mock_pub:
            from src.multi_tenant.middleware import invalidate_tenant_meta_cache

            invalidate_tenant_meta_cache("tenant-1", _publish=False)
            mock_pub.assert_not_called()

    def test_invalidate_full_flush_publishes(self):
        """invalidate_tenant_meta_cache(None) publishes full flush."""
        with patch(
            "src.multi_tenant.cache_invalidation.publish_cache_invalidation"
        ) as mock_pub:
            from src.multi_tenant.middleware import invalidate_tenant_meta_cache

            invalidate_tenant_meta_cache(None)
            mock_pub.assert_called_once_with(None)

    def test_shutdown_sets_event_and_clears_client(self):
        """shutdown_cache_invalidation sets shutdown event and clears state."""
        import src.multi_tenant.cache_invalidation as mod

        original_client = mod._redis_client
        original_thread = mod._subscriber_thread
        original_event = mod._shutdown_event

        mock_thread = MagicMock()
        mod._redis_client = MagicMock()
        mod._subscriber_thread = mock_thread
        mod._shutdown_event = threading.Event()

        try:
            mod.shutdown_cache_invalidation()
            assert mod._redis_client is None
            assert mod._subscriber_thread is None
            mock_thread.join.assert_called_once()
        finally:
            mod._redis_client = original_client
            mod._subscriber_thread = original_thread
            mod._shutdown_event = original_event


# =========================================================================
# SPEC-1758 — Pre-Auth Tracker LRU Cap
# =========================================================================

class TestPreAuthTrackerLRU:
    """SPEC-1758: Pre-auth rate limiter uses LRU eviction with cap."""

    def test_max_tracked_ips_default(self):
        """MAX_TRACKED_IPS defaults to 10000."""
        from src.multi_tenant.security_hardening import MAX_TRACKED_IPS

        assert MAX_TRACKED_IPS == 10000

    def test_trackers_is_ordered_dict(self):
        """PreAuthRateLimiter._trackers is an OrderedDict."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter()
        assert isinstance(limiter._trackers, OrderedDict)

    def test_record_failure_creates_tracker(self):
        """record_failure creates new tracker for unknown IP."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter()
        limiter.record_failure("10.0.0.1")
        assert "10.0.0.1" in limiter._trackers

    def test_lru_eviction_at_capacity(self):
        """Oldest entry evicted when tracker cap reached."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter(max_tracked_ips=3)
        limiter.record_failure("ip-1")
        limiter.record_failure("ip-2")
        limiter.record_failure("ip-3")
        # At capacity — next insert should evict ip-1
        limiter.record_failure("ip-4")
        assert "ip-1" not in limiter._trackers
        assert "ip-4" in limiter._trackers
        assert len(limiter._trackers) == 3

    def test_lru_access_on_is_blocked(self):
        """is_blocked moves IP to end of LRU order."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter(max_tracked_ips=3)
        limiter.record_failure("ip-1")
        limiter.record_failure("ip-2")
        limiter.record_failure("ip-3")
        # Access ip-1 — should move to end
        limiter.is_blocked("ip-1")
        # Now ip-2 is oldest
        limiter.record_failure("ip-4")
        assert "ip-2" not in limiter._trackers
        assert "ip-1" in limiter._trackers  # Preserved by LRU access

    def test_tracker_count_property(self):
        """tracker_count returns number of tracked IPs."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter()
        assert limiter.tracker_count == 0
        limiter.record_failure("ip-1")
        assert limiter.tracker_count == 1
        limiter.record_failure("ip-2")
        assert limiter.tracker_count == 2


# =========================================================================
# SPEC-1759 — TOCTOU Lock LRU Cap
# =========================================================================

class TestTOCTOULockLRU:
    """SPEC-1759: Per-tenant quick action locks use LRU eviction."""

    def test_max_tenant_locks_default(self):
        """MAX_TENANT_LOCKS defaults to 1000."""
        from src.multi_tenant.admin_quick_action_api import MAX_TENANT_LOCKS

        assert MAX_TENANT_LOCKS == 1000

    def test_tenant_qa_locks_is_ordered_dict(self):
        """_tenant_qa_locks is an OrderedDict."""
        from src.multi_tenant.admin_quick_action_api import _tenant_qa_locks

        assert isinstance(_tenant_qa_locks, OrderedDict)

    def test_get_tenant_lock_returns_lock(self):
        """_get_tenant_lock returns an asyncio.Lock."""
        from src.multi_tenant.admin_quick_action_api import _get_tenant_lock

        lock = _get_tenant_lock("test-tenant-lru-1")
        assert isinstance(lock, asyncio.Lock)
        # Cleanup
        from src.multi_tenant.admin_quick_action_api import _tenant_qa_locks

        _tenant_qa_locks.pop("test-tenant-lru-1", None)

    def test_get_tenant_lock_same_tenant_returns_same_lock(self):
        """Same tenant_id returns the same lock object."""
        from src.multi_tenant.admin_quick_action_api import (
            _get_tenant_lock,
            _tenant_qa_locks,
        )

        lock1 = _get_tenant_lock("test-tenant-lru-2")
        lock2 = _get_tenant_lock("test-tenant-lru-2")
        assert lock1 is lock2
        _tenant_qa_locks.pop("test-tenant-lru-2", None)

    def test_lock_lru_eviction_at_capacity(self):
        """Oldest lock evicted when MAX_TENANT_LOCKS reached."""
        from src.multi_tenant.admin_quick_action_api import (
            _get_tenant_lock,
            _tenant_qa_locks,
        )

        # Save original state
        original_locks = dict(_tenant_qa_locks)
        _tenant_qa_locks.clear()

        try:
            with patch(
                "src.multi_tenant.admin_quick_action_api.MAX_TENANT_LOCKS", 3
            ):
                _get_tenant_lock("t-1")
                _get_tenant_lock("t-2")
                _get_tenant_lock("t-3")
                assert len(_tenant_qa_locks) == 3
                _get_tenant_lock("t-4")
                assert "t-1" not in _tenant_qa_locks
                assert "t-4" in _tenant_qa_locks
                assert len(_tenant_qa_locks) == 3
        finally:
            _tenant_qa_locks.clear()
            _tenant_qa_locks.update(original_locks)

    def test_lock_lru_access_preserves_recent(self):
        """Accessing a lock moves it to end, preserving it from eviction."""
        from src.multi_tenant.admin_quick_action_api import (
            _get_tenant_lock,
            _tenant_qa_locks,
        )

        original_locks = dict(_tenant_qa_locks)
        _tenant_qa_locks.clear()

        try:
            with patch(
                "src.multi_tenant.admin_quick_action_api.MAX_TENANT_LOCKS", 3
            ):
                _get_tenant_lock("t-1")
                _get_tenant_lock("t-2")
                _get_tenant_lock("t-3")
                # Access t-1 to refresh it
                _get_tenant_lock("t-1")
                # Now t-2 is oldest
                _get_tenant_lock("t-4")
                assert "t-2" not in _tenant_qa_locks
                assert "t-1" in _tenant_qa_locks
        finally:
            _tenant_qa_locks.clear()
            _tenant_qa_locks.update(original_locks)


# =========================================================================
# SPEC-1760 — Health Metrics Endpoint
# =========================================================================

class TestHealthMetricsEndpoint:
    """SPEC-1760: /health/metrics with platform-admin-only auth."""

    def _make_metrics_app(self):
        """Create a minimal FastAPI app with health endpoints registered."""
        from fastapi import FastAPI
        from src.app.health import register_health_endpoints

        app = FastAPI()
        register_health_endpoints(app)
        return app

    def test_health_metrics_rejects_non_spa_key(self):
        """GET /health/metrics returns 403 without ar_spa_ prefix."""
        from starlette.testclient import TestClient

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_tenant_xyz"})
        assert response.status_code == 403
        assert "platform admin" in response.json()["error"].lower()

    def test_health_metrics_rejects_missing_key(self):
        """GET /health/metrics returns 403 with no API key."""
        from starlette.testclient import TestClient

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics")
        assert response.status_code == 403

    @patch("src.multi_tenant.repositories.platform_admin.PlatformAdminRepository")
    def test_health_metrics_reports_sse_connections(self, mock_repo_cls):
        """Health metrics response includes active_sse_connections and global_sse_limit."""
        from starlette.testclient import TestClient

        mock_repo = MagicMock()
        mock_repo.find_by_api_key_hash = AsyncMock(return_value={"is_active": True})
        mock_repo_cls.return_value = mock_repo

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_spa_test123"})
        assert response.status_code == 200
        data = response.json()
        assert "active_sse_connections" in data
        assert "global_sse_limit" in data
        assert isinstance(data["active_sse_connections"], int)
        assert data["global_sse_limit"] == 5000  # SPEC-1756 default

    @patch("src.multi_tenant.repositories.platform_admin.PlatformAdminRepository")
    def test_health_metrics_reports_event_loop_lag(self, mock_repo_cls):
        """Health metrics response includes event_loop_lag_ms >= 0."""
        from starlette.testclient import TestClient

        mock_repo = MagicMock()
        mock_repo.find_by_api_key_hash = AsyncMock(return_value={"is_active": True})
        mock_repo_cls.return_value = mock_repo

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_spa_test123"})
        assert response.status_code == 200
        data = response.json()
        assert "event_loop_lag_ms" in data
        assert data["event_loop_lag_ms"] >= 0

    @patch("src.multi_tenant.repositories.platform_admin.PlatformAdminRepository")
    def test_health_metrics_reports_uptime(self, mock_repo_cls):
        """Health metrics response includes uptime_seconds >= 0."""
        from starlette.testclient import TestClient

        mock_repo = MagicMock()
        mock_repo.find_by_api_key_hash = AsyncMock(return_value={"is_active": True})
        mock_repo_cls.return_value = mock_repo

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_spa_test123"})
        assert response.status_code == 200
        data = response.json()
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0

    @patch("src.multi_tenant.repositories.platform_admin.PlatformAdminRepository")
    def test_health_metrics_reports_pre_auth_tracker(self, mock_repo_cls):
        """Health metrics response includes pre_auth_tracker_count and limit."""
        from starlette.testclient import TestClient

        mock_repo = MagicMock()
        mock_repo.find_by_api_key_hash = AsyncMock(return_value={"is_active": True})
        mock_repo_cls.return_value = mock_repo

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_spa_test123"})
        assert response.status_code == 200
        data = response.json()
        assert "pre_auth_tracker_count" in data
        assert "pre_auth_tracker_limit" in data
        assert data["pre_auth_tracker_limit"] == 10000  # SPEC-1758 default

    @patch("src.multi_tenant.repositories.platform_admin.PlatformAdminRepository")
    def test_health_metrics_reports_tenant_locks(self, mock_repo_cls):
        """Health metrics response includes tenant_lock_count and limit."""
        from starlette.testclient import TestClient

        mock_repo = MagicMock()
        mock_repo.find_by_api_key_hash = AsyncMock(return_value={"is_active": True})
        mock_repo_cls.return_value = mock_repo

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_spa_test123"})
        assert response.status_code == 200
        data = response.json()
        assert "tenant_lock_count" in data
        assert "tenant_lock_limit" in data
        assert data["tenant_lock_limit"] == 1000  # SPEC-1759 default

    @patch("src.multi_tenant.repositories.platform_admin.PlatformAdminRepository")
    def test_health_metrics_reports_config_cache_ttl(self, mock_repo_cls):
        """Health metrics response includes config_cache_ttl_seconds == 300."""
        from starlette.testclient import TestClient

        mock_repo = MagicMock()
        mock_repo.find_by_api_key_hash = AsyncMock(return_value={"is_active": True})
        mock_repo_cls.return_value = mock_repo

        app = self._make_metrics_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/metrics", headers={"X-API-Key": "ar_spa_test123"})
        assert response.status_code == 200
        data = response.json()
        assert "config_cache_ttl_seconds" in data
        assert data["config_cache_ttl_seconds"] == 300  # SPEC-1748


# =========================================================================
# SPEC-1757 additional — Health endpoint cache invalidation status
# =========================================================================

class TestHealthCacheInvalidation:
    """SPEC-1757: Ready endpoint includes cache invalidation status."""

    def test_ready_endpoint_includes_cache_invalidation(self):
        """GET /ready response includes cache_invalidation.redis_pubsub boolean."""
        from fastapi import FastAPI
        from starlette.testclient import TestClient
        from src.app.health import register_health_endpoints

        app = FastAPI()
        register_health_endpoints(app)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "cache_invalidation" in data
        assert "redis_pubsub" in data["cache_invalidation"]
        assert isinstance(data["cache_invalidation"]["redis_pubsub"], bool)


# =========================================================================
# Lifecycle integration
# =========================================================================

class TestLifecycleIntegration:
    """SPEC-1757: Lifecycle startup/shutdown for cache invalidation."""

    def test_shutdown_handler_registered(self):
        """_shutdown_cache_invalidation is in the shutdown handler list."""
        from src.app.lifecycle import register_shutdown_handlers, _lifecycle_shutdown_handlers

        register_shutdown_handlers()
        # Verify the cache invalidation shutdown handler is in the list
        handler_names = [h.__name__ for h in _lifecycle_shutdown_handlers]
        assert "_shutdown_cache_invalidation" in handler_names

    @pytest.mark.asyncio
    async def test_startup_configures_cache_invalidation(self):
        """_startup_redis_rate_limiter calls configure_cache_invalidation when Redis available."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True

        mock_redis_mod = MagicMock()
        mock_redis_mod.Redis.from_url.return_value = mock_client

        with patch.dict(os.environ, {"REDIS_URL": "rediss://:fakekey@fakehost:6380/0"}), \
             patch.dict("sys.modules", {"redis": mock_redis_mod}), \
             patch("src.multi_tenant.security_hardening.RedisRateLimitBackend"), \
             patch("src.multi_tenant.security_hardening.set_rate_limit_backend"), \
             patch("src.multi_tenant.cache_invalidation.configure_cache_invalidation") as mock_configure:
            from src.app.lifecycle import _startup_redis_rate_limiter
            await _startup_redis_rate_limiter()
            mock_configure.assert_called_once_with(mock_client)

    def test_dockerfile_has_tini_entrypoint(self):
        """Dockerfile uses tini for proper signal handling with 4 workers."""
        dockerfile = open("Dockerfile").read()
        assert "tini" in dockerfile
        assert "ENTRYPOINT" in dockerfile
