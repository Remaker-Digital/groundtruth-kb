"""Tests for S132 code quality improvements (WI-0980 through WI-0986).

Covers all 7 findings from the independent code quality review:
    - WI-0980: PreAuth record_failure() wired on auth failure
    - WI-0981: SMTP sends offloaded to asyncio.to_thread()
    - WI-0982: Periodic PreAuth tracker cleanup
    - WI-0983: FastAPI lifespan migration (on_event → lifespan)
    - WI-0984: asyncio.Lock on TenantGate acquire()
    - WI-0985: Distributed rate limiting abstraction
    - WI-0986: Repository barrel re-export sync

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import re
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# WI-0980: PreAuth record_failure() wired on auth failure (SPEC-1621)
# ---------------------------------------------------------------------------


class TestPreAuthWiring:
    """Verify that TenantAuthMiddleware calls record_failure/record_success."""

    def test_middleware_dispatch_calls_record_failure_on_auth_error(self):
        """Auth failure branch must call get_pre_auth_limiter().record_failure()."""
        source = Path("src/multi_tenant/middleware.py").read_text()
        # Both AuthenticationError and generic Exception branches should record
        assert "get_pre_auth_limiter().record_failure(client_ip)" in source

    def test_middleware_dispatch_calls_record_success(self):
        """Successful auth must call record_success to reset failure counter."""
        source = Path("src/multi_tenant/middleware.py").read_text()
        assert "get_pre_auth_limiter().record_success(client_ip)" in source

    def test_middleware_extracts_client_ip(self):
        """Middleware must extract client IP from request scope."""
        source = Path("src/multi_tenant/middleware.py").read_text()
        assert 'client_ip = client[0] if client else "unknown"' in source

    def test_record_failure_called_in_both_exception_branches(self):
        """Both AuthenticationError and generic Exception must record failure."""
        source = Path("src/multi_tenant/middleware.py").read_text()
        # Count occurrences of record_failure in the dispatch method
        count = source.count("record_failure(client_ip)")
        assert count >= 2, f"Expected >=2 record_failure calls, found {count}"


# ---------------------------------------------------------------------------
# WI-0981: SMTP sends offloaded to asyncio.to_thread() (SPEC-1622)
# ---------------------------------------------------------------------------


class TestSmtpAsyncOffload:
    """Verify all SMTP send paths use asyncio.to_thread()."""

    SMTP_MODULES = [
        "src/multi_tenant/welcome_email.py",
        "src/multi_tenant/email_verification.py",
        "src/multi_tenant/magic_link_auth.py",
        "src/multi_tenant/trial_expiry_email.py",
        "src/multi_tenant/access_expiry_email.py",
        "src/multi_tenant/admin_contact_api.py",
        "src/multi_tenant/admin_apikey_api.py",
        "src/multi_tenant/alert_delivery.py",
        "src/multi_tenant/widget_otp_verification.py",
    ]

    @pytest.mark.parametrize("module_path", SMTP_MODULES)
    def test_smtp_module_uses_to_thread(self, module_path: str):
        """Each SMTP-using module must wrap blocking I/O with to_thread."""
        source = Path(module_path).read_text()
        if "smtplib" not in source:
            pytest.skip(f"{module_path} does not use smtplib")
        assert "asyncio.to_thread" in source, (
            f"{module_path} uses smtplib but does not wrap with asyncio.to_thread()"
        )

    @pytest.mark.parametrize("module_path", SMTP_MODULES)
    def test_smtp_module_has_inner_function(self, module_path: str):
        """SMTP modules should define an inner _smtp_send function."""
        source = Path(module_path).read_text()
        if "smtplib" not in source:
            pytest.skip(f"{module_path} does not use smtplib")
        # Either inner function pattern or whole-function offload via to_thread
        has_inner = "_smtp_send" in source
        has_to_thread_call = "to_thread(" in source
        assert has_inner or has_to_thread_call, (
            f"{module_path} must use inner _smtp_send() or asyncio.to_thread()"
        )

    def test_standalone_auth_reset_email_offloaded(self):
        """standalone_auth.py must offload _send_admin_reset_email to thread."""
        source = Path("src/app/standalone_auth.py").read_text()
        assert "asyncio.to_thread(_send_admin_reset_email" in source

    def test_standalone_auth_password_changed_email_offloaded(self):
        """standalone_auth.py must offload _send_admin_password_changed_email."""
        source = Path("src/app/standalone_auth.py").read_text()
        assert "asyncio.to_thread(_send_admin_password_changed_email" in source


# ---------------------------------------------------------------------------
# WI-0982: Periodic PreAuth tracker cleanup (SPEC-1623)
# ---------------------------------------------------------------------------


class TestPreAuthCleanup:
    """Verify the pre-auth cleanup background task infrastructure."""

    def test_cleanup_loop_exists(self):
        """A _pre_auth_cleanup_loop coroutine must exist."""
        from src.multi_tenant.security_hardening import _pre_auth_cleanup_loop

        assert inspect.iscoroutinefunction(_pre_auth_cleanup_loop)

    def test_start_stop_functions_exist(self):
        """start_pre_auth_cleanup and stop_pre_auth_cleanup must exist."""
        from src.multi_tenant.security_hardening import (
            start_pre_auth_cleanup,
            stop_pre_auth_cleanup,
        )

        assert inspect.iscoroutinefunction(start_pre_auth_cleanup)
        assert inspect.iscoroutinefunction(stop_pre_auth_cleanup)

    def test_cleanup_interval_is_reasonable(self):
        """Cleanup interval should be between 60 and 600 seconds."""
        from src.multi_tenant.security_hardening import _CLEANUP_INTERVAL_SECONDS

        assert 60 <= _CLEANUP_INTERVAL_SECONDS <= 600

    def test_lifecycle_wires_cleanup(self):
        """lifecycle.py must include pre-auth cleanup in handlers."""
        source = Path("src/app/lifecycle.py").read_text()
        assert "_startup_pre_auth_cleanup" in source
        assert "_shutdown_pre_auth_cleanup" in source

    def test_pre_auth_limiter_cleanup_method(self):
        """PreAuthRateLimiter must have a cleanup() method."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter()
        assert hasattr(limiter, "cleanup")
        # Cleanup on empty should return 0
        assert limiter.cleanup() == 0

    def test_pre_auth_cleanup_removes_expired(self):
        """cleanup() should remove trackers whose entries have all expired."""
        from src.multi_tenant.security_hardening import PreAuthRateLimiter

        limiter = PreAuthRateLimiter(window_seconds=1, block_seconds=1)
        limiter.record_failure("1.2.3.4")

        # Immediately — should not clean up (still within window)
        assert limiter.cleanup() == 0

        # Manually expire entries by manipulating timestamps
        for tracker in limiter._trackers.values():
            tracker.timestamps = [time.monotonic() - 10]
            tracker.blocked_until = 0.0

        removed = limiter.cleanup()
        assert removed == 1


# ---------------------------------------------------------------------------
# WI-0983: FastAPI lifespan migration (SPEC-1623)
# ---------------------------------------------------------------------------


class TestLifespanMigration:
    """Verify the on_event → lifespan migration is complete."""

    def test_no_on_event_in_lifecycle(self):
        """lifecycle.py must NOT use app.on_event() for registration."""
        source = Path("src/app/lifecycle.py").read_text()
        # Find actual on_event() CALLS — e.g. app.on_event("startup")
        # Exclude docstrings/comments that merely reference the pattern
        calls = re.findall(r'^\s*\w+\.on_event\(', source, re.MULTILINE)
        assert len(calls) == 0, (
            f"lifecycle.py still uses on_event() calls: {calls}"
        )

    def test_no_on_event_in_background(self):
        """background.py must NOT use app.on_event() for registration."""
        source = Path("src/app/background.py").read_text()
        calls = re.findall(r'^\s*\w+\.on_event\(', source, re.MULTILINE)
        assert len(calls) == 0, (
            f"background.py still uses on_event() calls: {calls}"
        )

    def test_build_app_lifespan_exists(self):
        """build_app_lifespan() must exist and return a callable."""
        from src.app.lifecycle import build_app_lifespan

        lifespan = build_app_lifespan()
        assert callable(lifespan)

    def test_main_uses_lifespan(self):
        """main.py must pass lifespan to create_app()."""
        source = Path("src/main.py").read_text()
        assert "create_app(lifespan=build_app_lifespan())" in source

    def test_factory_accepts_lifespan(self):
        """create_app() must accept a lifespan parameter."""
        from src.app.factory import create_app

        sig = inspect.signature(create_app)
        assert "lifespan" in sig.parameters

    def test_handler_registries_populated(self):
        """register_startup_handlers() must populate the handler list."""
        from src.app.lifecycle import (
            _lifecycle_startup_handlers,
            _lifecycle_shutdown_handlers,
            register_startup_handlers,
            register_shutdown_handlers,
        )

        register_startup_handlers()
        register_shutdown_handlers()
        assert len(_lifecycle_startup_handlers) > 30, (
            f"Expected >30 startup handlers, got {len(_lifecycle_startup_handlers)}"
        )
        assert len(_lifecycle_shutdown_handlers) >= 5, (
            f"Expected >=5 shutdown handlers, got {len(_lifecycle_shutdown_handlers)}"
        )

    def test_background_registries_populated(self):
        """Background register_* functions must populate handler lists."""
        from src.app.background import (
            _bg_startup_handlers,
            _bg_shutdown_handlers,
            register_idle_scanner,
        )

        initial_start = len(_bg_startup_handlers)
        initial_stop = len(_bg_shutdown_handlers)
        register_idle_scanner()
        assert len(_bg_startup_handlers) == initial_start + 1
        assert len(_bg_shutdown_handlers) == initial_stop + 1

    def test_handler_collection_before_app_creation(self):
        """main.py must call register_* BEFORE create_app()."""
        source = Path("src/main.py").read_text()
        register_pos = source.index("register_startup_handlers()")
        app_pos = source.index("app = create_app(")
        assert register_pos < app_pos, (
            "Handler registration must happen before app creation"
        )


# ---------------------------------------------------------------------------
# WI-0984: asyncio.Lock on TenantGate acquire() (SPEC-1625)
# ---------------------------------------------------------------------------


class TestTenantGateLock:
    """Verify TenantGate uses asyncio.Lock for atomic check-and-increment."""

    def test_tenant_gate_has_queue_lock(self):
        """_TenantGate must have an asyncio.Lock attribute."""
        from src.multi_tenant.pipeline_resilience import _TenantGate

        gate = _TenantGate(max_concurrent=5, queue_depth=10)
        assert hasattr(gate, "_queue_lock")
        assert isinstance(gate._queue_lock, asyncio.Lock)

    def test_acquire_uses_lock(self):
        """acquire() method must use 'async with self._queue_lock'."""
        source = Path("src/multi_tenant/pipeline_resilience.py").read_text(encoding="utf-8")
        # Find the acquire method and check for lock usage
        assert "async with self._queue_lock:" in source

    @pytest.mark.asyncio
    async def test_acquire_returns_true_when_available(self):
        """acquire() should return True when slots are available."""
        from src.multi_tenant.pipeline_resilience import _TenantGate

        gate = _TenantGate(max_concurrent=2, queue_depth=2)
        acquired = await gate.acquire()
        assert acquired is True
        gate.release()

    @pytest.mark.asyncio
    async def test_acquire_returns_false_when_full(self):
        """acquire() should return False when gate is completely full."""
        from src.multi_tenant.pipeline_resilience import _TenantGate

        gate = _TenantGate(max_concurrent=1, queue_depth=0)
        # Acquire the one available slot
        first = await gate.acquire()
        assert first is True
        # Now the gate should be full
        second = await gate.acquire()
        assert second is False
        gate.release()


# ---------------------------------------------------------------------------
# WI-0985: Distributed rate limiting abstraction (SPEC-1626)
# ---------------------------------------------------------------------------


class TestRateLimitAbstraction:
    """Verify the pluggable rate limiting backend infrastructure."""

    def test_rate_limit_backend_base_class_exists(self):
        """RateLimitBackend abstract base class must exist."""
        from src.multi_tenant.security_hardening import RateLimitBackend

        backend = RateLimitBackend()
        with pytest.raises(NotImplementedError):
            backend.is_limited("key", max_requests=5, window_seconds=60)
        with pytest.raises(NotImplementedError):
            backend.reset("key")
        with pytest.raises(NotImplementedError):
            backend.cleanup()

    def test_in_memory_backend_exists(self):
        """InMemoryRateLimitBackend must implement the protocol."""
        from src.multi_tenant.security_hardening import (
            InMemoryRateLimitBackend,
            RateLimitBackend,
        )

        backend = InMemoryRateLimitBackend()
        assert isinstance(backend, RateLimitBackend)

    def test_in_memory_backend_rate_limiting(self):
        """InMemoryRateLimitBackend must enforce sliding window limits."""
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend

        backend = InMemoryRateLimitBackend()

        # First 3 requests should succeed
        for _ in range(3):
            assert backend.is_limited("test-key", max_requests=3, window_seconds=300) is False

        # 4th request should be limited
        assert backend.is_limited("test-key", max_requests=3, window_seconds=300) is True

    def test_in_memory_backend_reset(self):
        """reset() should clear rate limit state for a key."""
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend

        backend = InMemoryRateLimitBackend()
        backend.is_limited("test-key", max_requests=1, window_seconds=300)

        # Should be limited now
        assert backend.is_limited("test-key", max_requests=1, window_seconds=300) is True

        # Reset and retry
        backend.reset("test-key")
        assert backend.is_limited("test-key", max_requests=1, window_seconds=300) is False

    def test_in_memory_backend_cleanup(self):
        """cleanup() should remove expired entries."""
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend

        backend = InMemoryRateLimitBackend()
        backend.is_limited("test-key", max_requests=10, window_seconds=300)

        # Manually expire entries
        backend._windows["test-key"] = [time.time() - 700]

        removed = backend.cleanup()
        assert removed >= 1

    def test_get_set_rate_limit_backend(self):
        """get/set_rate_limit_backend must manage the singleton."""
        from src.multi_tenant.security_hardening import (
            InMemoryRateLimitBackend,
            get_rate_limit_backend,
            set_rate_limit_backend,
        )

        # Get should return InMemory by default
        backend = get_rate_limit_backend()
        assert isinstance(backend, InMemoryRateLimitBackend)

        # Set a custom backend
        custom = InMemoryRateLimitBackend()
        set_rate_limit_backend(custom)
        assert get_rate_limit_backend() is custom

        # Reset to default for other tests
        set_rate_limit_backend(InMemoryRateLimitBackend())

    def test_different_keys_independent(self):
        """Different keys must have independent rate limits."""
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend

        backend = InMemoryRateLimitBackend()
        backend.is_limited("key-a", max_requests=1, window_seconds=300)

        # key-a should be limited, key-b should not
        assert backend.is_limited("key-a", max_requests=1, window_seconds=300) is True
        assert backend.is_limited("key-b", max_requests=1, window_seconds=300) is False


# ---------------------------------------------------------------------------
# WI-0986: Repository barrel re-export sync (SPEC-1627)
# ---------------------------------------------------------------------------


class TestRepositoryBarrelSync:
    """Verify repository.py and repositories/__init__.py stay in sync."""

    def test_barrel_exports_all_package_names(self):
        """repository.py __all__ must include every name from repositories __all__."""
        # Read both __all__ lists
        import src.multi_tenant.repository as barrel
        import src.multi_tenant.repositories as package

        barrel_all = set(barrel.__all__)
        package_all = set(package.__all__)

        missing = package_all - barrel_all
        assert not missing, (
            f"repository.py barrel missing exports from repositories/: {missing}"
        )

    def test_barrel_can_import_all_names(self):
        """Every name in repositories/__all__ must be importable from barrel."""
        import src.multi_tenant.repositories as package

        for name in package.__all__:
            obj = getattr(package, name)
            # Verify the same object is available from the barrel
            from src.multi_tenant import repository as barrel
            barrel_obj = getattr(barrel, name, None)
            assert barrel_obj is not None, (
                f"{name} in repositories/ but not importable from repository.py"
            )

    def test_incident_and_alert_repos_in_barrel(self):
        """Newer repos (Incident, AlertRule, AlertHistory) must be in barrel."""
        from src.multi_tenant.repository import (
            AlertHistoryRepository,
            AlertRuleRepository,
            IncidentRepository,
        )

        assert AlertHistoryRepository is not None
        assert AlertRuleRepository is not None
        assert IncidentRepository is not None

    def test_sync_notice_comment_exists(self):
        """repository.py must contain a sync notice referencing SPEC-1627."""
        source = Path("src/multi_tenant/repository.py").read_text()
        assert "SPEC-1627" in source
        assert "SYNC NOTICE" in source or "sync" in source.lower()
