"""Regression test configuration for production upgrade validation.

These tests run against a LIVE production endpoint to validate that an
upgrade has not broken any critical functionality. They are designed to
be safe to run against production (read-only where possible, cleanup
after write operations).

Usage:
    # Set the production URL (or defaults to env var PROD_URL)
    export PROD_URL=https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io

    # Run all regression tests
    python -m pytest tests/regression/ -x -q --tb=short

    # Run only Tier 0 (blocking) tests
    python -m pytest tests/regression/ -x -q -m tier0

    # Run Tier 0 + Tier 1 (pre-launch gate)
    python -m pytest tests/regression/ -x -q -m "tier0 or tier1"
"""

import os

import pytest
import httpx

# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# ---------------------------------------------------------------------------
# Auto-load .env.local (transient credentials must never be hardcoded —
# see REPEATABLE-PROCEDURES.md Section 7: No Hardcoded Transient Values)
# ---------------------------------------------------------------------------
# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local
load_env_local()

# Production URL — default per REPEATABLE-PROCEDURES.md §7.4 — .env.local takes precedence
PROD_URL = os.environ.get(
    "PROD_URL",
    "",  # SPEC-0058: No hardcoded FQDNs — set PROD_URL env var
)

# Widget key — loaded from .env.local PREVIEW_WIDGET_KEY or WIDGET_KEY env var.
# No hardcoded fallback: transient credentials must come from env/config.
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY") or os.environ.get("WIDGET_KEY", "")

# API key for admin operations (optional — some tests skip without it)
API_KEY = os.environ.get("SUPERADMIN_PREVIEW_API_KEY") or os.environ.get("AGENTRED_API_KEY", "")


@pytest.fixture(scope="session")
def prod_url():
    """Production base URL."""
    return PROD_URL


def _check_production_reachable() -> bool:
    """Quick connectivity check — returns False if production is unreachable."""
    try:
        with httpx.Client(timeout=5.0) as c:
            resp = c.get(f"{PROD_URL}/health")
            return resp.status_code == 200
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, Exception):
        return False


@pytest.fixture(scope="session")
def client():
    """Shared httpx client for all regression tests.

    Skips the entire session if the production endpoint is unreachable.
    """
    if not _check_production_reachable():
        pytest.skip(
            f"Production endpoint unreachable at {PROD_URL} — "
            "skipping regression tests (API Gateway may be down or subscription suspended)"
        )
    with httpx.Client(base_url=PROD_URL, timeout=30.0, follow_redirects=True) as c:
        yield c


@pytest.fixture(scope="session")
def async_client():
    """Async httpx client for SSE and streaming tests."""
    # Note: Use as context manager in individual tests
    return httpx.AsyncClient(base_url=PROD_URL, timeout=30.0, follow_redirects=True)


@pytest.fixture(scope="session")
def widget_key():
    """Widget key for chat API authentication."""
    return WIDGET_KEY


@pytest.fixture(scope="session")
def api_key():
    """API key for admin operations. Tests that need this should skip if empty."""
    return API_KEY


@pytest.fixture(scope="session")
def admin_headers(api_key):
    """Headers for admin API calls."""
    if not api_key:
        pytest.skip("AGENTRED_API_KEY not set — skipping admin API tests")
    return {"X-API-Key": api_key}


@pytest.fixture(scope="session")
def widget_headers(widget_key):
    """Headers for widget/chat API calls."""
    return {"X-Widget-Key": widget_key}
