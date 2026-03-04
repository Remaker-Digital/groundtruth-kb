"""Shared fixtures for live API tests (SPEC-1649: external interfaces only).

These tests use httpx to call real staging/production endpoints.
No mocks, no stubs, no source inspection — only live HTTP requests.

Environment variables (auto-loaded from .env.local, overridable via env):
    PROD_URL                     — Base URL (default: production FQDN)
    SUPERADMIN_PREVIEW_API_KEY   — Admin API key
    PREVIEW_WIDGET_KEY           — Widget publishable key

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import time

import httpx
import pytest

# ---------------------------------------------------------------------------
# Auto-load .env.local (transient credentials)
# ---------------------------------------------------------------------------
from scripts._env import load_env_local

load_env_local()

# ---------------------------------------------------------------------------
# Constants — resolved from env vars with fallbacks
# ---------------------------------------------------------------------------
PROD_URL = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
)

# Widget key for conversation tests
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")
if not WIDGET_KEY:
    try:
        from scripts.upgrade_verification import ENVIRONMENTS
        _prod = ENVIRONMENTS.get("production", {})
        WIDGET_KEY = _prod.get("widget_key", "")
    except ImportError:
        pass

# Admin API key
API_KEY = os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")
if not API_KEY:
    try:
        from scripts.upgrade_verification import ENVIRONMENTS  # type: ignore[no-redef]
        _prod = ENVIRONMENTS.get("production", {})
        API_KEY = _prod.get("api_key", "")
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for API calls."""
    return PROD_URL


@pytest.fixture(scope="session")
def widget_key() -> str:
    """Return the widget publishable key, skip if unavailable."""
    if not WIDGET_KEY:
        pytest.skip(
            "No widget key found "
            "(set PREVIEW_WIDGET_KEY or configure scripts/upgrade_verification.py) — "
            "skipping live API tests"
        )
    return WIDGET_KEY


@pytest.fixture(scope="session")
def api_key() -> str:
    """Return the admin API key, skip if unavailable."""
    if not API_KEY:
        pytest.skip(
            "No API key found "
            "(set SUPERADMIN_PREVIEW_API_KEY) — "
            "skipping live API tests"
        )
    return API_KEY


@pytest.fixture(scope="session")
def live_client(base_url: str) -> httpx.Client:
    """Create a shared httpx client for the test session."""
    client = httpx.Client(
        base_url=base_url,
        timeout=30.0,
        follow_redirects=True,
    )
    yield client  # type: ignore[misc]
    client.close()


@pytest.fixture(scope="session")
def platform_reachable(live_client: httpx.Client) -> None:
    """Skip all tests if the platform is unreachable."""
    try:
        resp = live_client.get("/health")
        if resp.status_code != 200:
            pytest.skip(f"Platform unreachable: GET /health returned {resp.status_code}")
    except Exception as e:
        pytest.skip(f"Platform unreachable: {e}")


@pytest.fixture(autouse=True, scope="class")
def _rate_limit_cooldown():
    """Insert a 2s cooldown between test classes to stay within rate limits."""
    yield
    time.sleep(2)
