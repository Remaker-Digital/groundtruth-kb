"""Auth interceptor regression tests.

Verifies that all admin console apiFetch wrappers intercept 401/403
responses and redirect to the authentication gate. This prevents
bookmarked URLs from showing raw error messages when sessions expire.

Fix history:
  - S210: Standalone admin showed "Tenant lookup failed: 400" for
    expired session bookmarks. Fixed by adding 400→onLogout in
    StandaloneLayout.tsx resolveTenant(), then adding global
    401/403 interceptors to all three apiFetch wrappers.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / "admin"


def _read(path: Path) -> str:
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Standalone admin — StandaloneLayout.tsx
# ---------------------------------------------------------------------------


class TestStandaloneAuthInterceptor:
    """Standalone admin must redirect to login on auth failures."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(
            ADMIN / "standalone" / "layouts" / "StandaloneLayout.tsx"
        )

    def test_apifetch_intercepts_401(self) -> None:
        """apiFetch must check resp.status === 401."""
        assert "resp.status === 401" in self.source, (
            "Standalone apiFetch must intercept 401 responses"
        )

    def test_apifetch_intercepts_403(self) -> None:
        """apiFetch must check resp.status === 403."""
        assert "resp.status === 403" in self.source, (
            "Standalone apiFetch must intercept 403 responses"
        )

    def test_apifetch_calls_onlogout(self) -> None:
        """apiFetch 401/403 handler must call onLogout()."""
        # Find the apiFetch function and verify it references onLogout
        match = re.search(
            r"const apiFetch.*?onLogout\(\)",
            self.source,
            re.DOTALL,
        )
        assert match, (
            "Standalone apiFetch must call onLogout() on auth failure"
        )

    def test_resolve_tenant_intercepts_400(self) -> None:
        """resolveTenant must redirect on 400 (expired session bookmark)."""
        assert "resp.status === 400" in self.source, (
            "resolveTenant must intercept 400 responses (expired session)"
        )


# ---------------------------------------------------------------------------
# Provider admin — ProviderLayout.tsx
# ---------------------------------------------------------------------------


class TestProviderAuthInterceptor:
    """Provider admin must redirect to login on auth failures."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(
            ADMIN / "provider" / "layouts" / "ProviderLayout.tsx"
        )

    def test_apifetch_intercepts_401(self) -> None:
        """apiFetch must check resp.status === 401."""
        assert "resp.status === 401" in self.source, (
            "Provider apiFetch must intercept 401 responses"
        )

    def test_apifetch_intercepts_403(self) -> None:
        """apiFetch must check resp.status === 403."""
        assert "resp.status === 403" in self.source, (
            "Provider apiFetch must intercept 403 responses"
        )

    def test_apifetch_calls_onlogout(self) -> None:
        """apiFetch 401/403 handler must call onLogout()."""
        match = re.search(
            r"const apiFetch.*?onLogout\(\)",
            self.source,
            re.DOTALL,
        )
        assert match, (
            "Provider apiFetch must call onLogout() on auth failure"
        )


# ---------------------------------------------------------------------------
# Shopify admin — ShopifyAppLayout.tsx
# ---------------------------------------------------------------------------


class TestShopifyAuthInterceptor:
    """Shopify admin must re-auth on auth failures."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(
            ADMIN / "shopify" / "layouts" / "ShopifyAppLayout.tsx"
        )

    def test_apifetch_intercepts_401(self) -> None:
        """apiFetch must check resp.status === 401."""
        assert "resp.status === 401" in self.source, (
            "Shopify apiFetch must intercept 401 responses"
        )

    def test_apifetch_intercepts_403(self) -> None:
        """apiFetch must check resp.status === 403."""
        assert "resp.status === 403" in self.source, (
            "Shopify apiFetch must intercept 403 responses"
        )

    def test_apifetch_reloads_on_auth_failure(self) -> None:
        """Shopify apiFetch must reload for app bridge re-auth."""
        match = re.search(
            r"const apiFetch.*?window\.location\.reload\(\)",
            self.source,
            re.DOTALL,
        )
        assert match, (
            "Shopify apiFetch must call window.location.reload() on auth failure"
        )
