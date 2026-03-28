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

# Tenant API key for tenant-scoped admin endpoints (SPEC-1644 compliance).
# These endpoints require ?tenant= AND a tenant-scoped key (ar_live_*).
# SPA keys (ar_spa_*) authenticate but have no tenant role → 401 on /api/admin/*.
TENANT_KEY = os.environ.get("STAGING_REMAKER_TENANT_KEY", "")
TENANT_ID = os.environ.get("STAGING_TENANT_ID", "remaker-digital-001")


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


def _check_credentials_valid() -> dict[str, str]:
    """Preflight probe: test each credential against a lightweight endpoint.

    Returns a dict of {credential_name: problem_description} for any stale
    or invalid credentials. Empty dict = all credentials valid.
    """
    problems: dict[str, str] = {}
    if not PROD_URL:
        return problems  # Can't probe without a URL

    try:
        with httpx.Client(timeout=5.0) as c:
            # Widget key probe
            if WIDGET_KEY:
                try:
                    resp = c.get(
                        f"{PROD_URL}/api/config",
                        params={"page_type": "index"},
                        headers={"X-Widget-Key": WIDGET_KEY},
                    )
                    if resp.status_code in (401, 403):
                        problems["WIDGET_KEY"] = f"returned {resp.status_code} — credential is stale or invalid"
                except Exception:
                    pass  # Network error, not a credential problem

            # Admin key probe
            if API_KEY:
                try:
                    resp = c.get(
                        f"{PROD_URL}/api/superadmin/dashboard",
                        headers={"X-API-Key": API_KEY},
                    )
                    if resp.status_code in (401, 403):
                        problems["API_KEY"] = f"returned {resp.status_code} — credential is stale or invalid"
                except Exception:
                    pass

            # Tenant key probe
            if TENANT_KEY and TENANT_ID:
                try:
                    resp = c.get(
                        f"{PROD_URL}/api/admin/team",
                        params={"tenant": TENANT_ID},
                        headers={"X-API-Key": TENANT_KEY},
                    )
                    if resp.status_code in (401, 403):
                        problems["TENANT_KEY"] = f"returned {resp.status_code} — credential is stale or invalid"
                except Exception:
                    pass
    except Exception:
        pass  # Can't probe, don't block

    return problems


@pytest.fixture(scope="session")
def client():
    """Shared httpx client for all regression tests.

    Skips the entire session if the production endpoint is unreachable.
    Warns if any credentials are stale (WI-1642 preflight validation).
    """
    if not _check_production_reachable():
        pytest.skip(
            f"Production endpoint unreachable at {PROD_URL} — "
            "skipping regression tests (API Gateway may be down or subscription suspended)"
        )

    # WI-1642: Credential preflight — detect stale credentials early
    stale = _check_credentials_valid()
    if stale:
        summary = "; ".join(f"{k}: {v}" for k, v in stale.items())
        import warnings
        warnings.warn(
            f"Stale test credentials detected (WI-1642): {summary}. "
            "Tests requiring these credentials will be skipped. "
            "Refresh credentials from Key Vault — see REPEATABLE-PROCEDURES.md Section 7.",
            stacklevel=1,
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
    """Headers for SPA platform admin API calls (/api/superadmin/*)."""
    if not api_key:
        pytest.skip("SUPERADMIN_PREVIEW_API_KEY not set — skipping admin API tests")
    return {"X-API-Key": api_key}


@pytest.fixture(scope="session")
def tenant_key():
    """Tenant API key for tenant-scoped admin endpoints."""
    return TENANT_KEY


@pytest.fixture(scope="session")
def tenant_admin_headers(tenant_key):
    """Headers for tenant-scoped admin API calls (/api/admin/*, /api/dashboard/*).

    SPEC-1644: Tenant keys (ar_live_*) require ?tenant= in the URL.
    SPA keys cannot access tenant-scoped endpoints.
    """
    if not tenant_key:
        pytest.skip("STAGING_REMAKER_TENANT_KEY not set — skipping tenant admin tests")
    return {"X-API-Key": tenant_key}


@pytest.fixture(scope="session")
def tenant_id():
    """Tenant ID for SPEC-1644 ?tenant= URL parameter."""
    return TENANT_ID


@pytest.fixture(scope="session")
def widget_headers(widget_key):
    """Headers for widget/chat API calls.

    Skips tests if WIDGET_KEY is not set (WI-1642 credential preflight).
    """
    if not widget_key:
        pytest.skip("WIDGET_KEY not set — skipping widget API tests")
    return {"X-Widget-Key": widget_key}


@pytest.fixture(scope="session")
def credential_status():
    """Exposes credential preflight results to individual tests.

    Tests can use this to skip gracefully when their specific credential is stale:
        if 'WIDGET_KEY' in credential_status:
            pytest.skip(credential_status['WIDGET_KEY'])
    """
    return _check_credentials_valid() if PROD_URL else {}
