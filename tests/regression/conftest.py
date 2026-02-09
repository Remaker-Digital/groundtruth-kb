"""Regression test configuration for production upgrade validation.

These tests run against a LIVE production endpoint to validate that an
upgrade has not broken any critical functionality. They are designed to
be safe to run against production (read-only where possible, cleanup
after write operations).

Usage:
    # Set the production URL (or defaults to env var PROD_URL)
    export PROD_URL=https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io

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

# Production URL — set via PROD_URL env var or default to production FQDN
PROD_URL = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io"
)

# Widget key for tenant remaker-digital-001 (from MEMORY.md)
WIDGET_KEY = os.environ.get("WIDGET_KEY", "pk_live_c79a2bd0_dcbf0c6f")

# API key for admin operations (optional — some tests skip without it)
API_KEY = os.environ.get("AGENTRED_API_KEY", "")


@pytest.fixture(scope="session")
def prod_url():
    """Production base URL."""
    return PROD_URL


@pytest.fixture(scope="session")
def client():
    """Shared httpx client for all regression tests."""
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
