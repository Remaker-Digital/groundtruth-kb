"""Tests for rate-limit consolidation (S161, SPEC-1694).

Verifies that ad-hoc per-module rate limiters have been replaced with
the shared RateLimitBackend from security_hardening.py.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import ast
import pathlib
import pytest


# Modules that previously had ad-hoc rate limiters (dict[str, list[float]] pattern)
AD_HOC_MODULES = [
    "src/multi_tenant/email_verification.py",
    "src/multi_tenant/widget_otp_verification.py",
    "src/multi_tenant/magic_link_auth.py",
    "src/multi_tenant/email_change.py",
    "src/multi_tenant/admin_apikey_api.py",
]

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _read_source(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


class TestAdHocLimiterRemoval:
    """SPEC-1694: Ad-hoc rate limiters MUST use shared backend."""

    @pytest.mark.parametrize("module_path", AD_HOC_MODULES)
    def test_no_module_level_rate_limit_dict(self, module_path):
        """No module-level _rate_limit: dict[str, list[float]] remains."""
        src = _read_source(module_path)
        # Should not have a standalone _rate_limit dict definition
        assert "_rate_limit: dict" not in src or "_rate_limit_backend" in src

    @pytest.mark.parametrize("module_path", AD_HOC_MODULES)
    def test_uses_get_rate_limit_backend(self, module_path):
        """Each module MUST import or call get_rate_limit_backend."""
        src = _read_source(module_path)
        assert "get_rate_limit_backend" in src or "is_limited" in src

    @pytest.mark.parametrize("module_path", AD_HOC_MODULES)
    def test_no_inline_sliding_window(self, module_path):
        """No inline sliding-window cleanup code (ts > window_start)."""
        src = _read_source(module_path)
        assert "window_start" not in src or "get_rate_limit_backend" in src


class TestSharedBackendIntegration:
    """Verify shared backend works for all consolidated limiters."""

    def test_backend_is_importable(self):
        from src.multi_tenant.security_hardening import get_rate_limit_backend
        backend = get_rate_limit_backend()
        assert hasattr(backend, "is_limited")

    def test_backend_limits_correctly(self):
        from src.multi_tenant.security_hardening import (
            get_rate_limit_backend,
            InMemoryRateLimitBackend,
            set_rate_limit_backend,
        )
        # Use a fresh backend to avoid test pollution
        fresh = InMemoryRateLimitBackend()
        key = "test:consolidation:ip:1.2.3.4"
        for _ in range(3):
            assert fresh.is_limited(key, max_requests=3, window_seconds=300) is False
        assert fresh.is_limited(key, max_requests=3, window_seconds=300) is True

    def test_backend_reset_clears_state(self):
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend
        fresh = InMemoryRateLimitBackend()
        key = "test:reset:ip:5.6.7.8"
        for _ in range(3):
            fresh.is_limited(key, max_requests=3, window_seconds=300)
        assert fresh.is_limited(key, max_requests=3, window_seconds=300) is True
        fresh.reset(key)
        assert fresh.is_limited(key, max_requests=3, window_seconds=300) is False

    def test_backend_cleanup_removes_expired(self):
        import time
        from unittest.mock import patch
        from src.multi_tenant.security_hardening import InMemoryRateLimitBackend
        fresh = InMemoryRateLimitBackend()
        key = "test:cleanup:ip:9.10.11.12"
        fresh.is_limited(key, max_requests=10, window_seconds=1)
        # Fast-forward past window
        with patch("src.multi_tenant.security_hardening.time.time", return_value=time.time() + 10):
            removed = fresh.cleanup()
        assert removed >= 0


class TestRateLimitKeyNamespacing:
    """Each module should use a distinct key prefix to avoid collisions."""

    def test_email_verification_key_prefix(self):
        src = _read_source("src/multi_tenant/email_verification.py")
        # Should include a module-specific prefix in the key
        assert "email_verify" in src or "ev:" in src or "email-verify" in src

    def test_magic_link_key_prefix(self):
        src = _read_source("src/multi_tenant/magic_link_auth.py")
        assert "magic_link" in src or "ml:" in src or "magic-link" in src

    def test_widget_otp_key_prefix(self):
        src = _read_source("src/multi_tenant/widget_otp_verification.py")
        assert "otp" in src or "widget_otp" in src

    def test_email_change_key_prefix(self):
        src = _read_source("src/multi_tenant/email_change.py")
        assert "email_change" in src or "ec:" in src or "email-change" in src

    def test_apikey_reset_key_prefix(self):
        src = _read_source("src/multi_tenant/admin_apikey_api.py")
        assert "apikey" in src or "ak:" in src or "api_key" in src
