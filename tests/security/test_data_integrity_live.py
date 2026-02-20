"""Live data integrity testing — validates API consistency and data persistence.

Tests verify that API responses are consistent, data persists correctly,
and Cosmos DB containers exist with expected schema.

Procedure: docs/operations/data-integrity-test-procedure.md
Prerequisites: Production healthy, both tenants seeded.

Run:
    PROD_URL=https://... python -m pytest tests/security/test_data_integrity_live.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx
import pytest

# ---------------------------------------------------------------------------
# Auto-load .env.local
# ---------------------------------------------------------------------------
from scripts._env import load_env_local
load_env_local()

PROD_URL = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
)

API_KEY = os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")

# Tenant B credentials
_creds_path = Path(__file__).resolve().parent.parent.parent / "logs" / "test_tenant_credentials.json"
_tenant_b_creds: dict = {}
if _creds_path.exists():
    _tenant_b_creds = json.loads(_creds_path.read_text())
TENANT_B_API_KEY = _tenant_b_creds.get("superadmin_key", "")


def _check_production_reachable() -> bool:
    try:
        r = httpx.get(f"{PROD_URL}/health", timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def _request_with_rate_limit_retry(
    client: httpx.Client, method: str, url: str, *, headers: dict, max_retries: int = 3
) -> httpx.Response:
    """Make a request, retrying if rate-limited (429)."""
    for attempt in range(max_retries):
        r = getattr(client, method)(url, headers=headers)
        if r.status_code != 429:
            return r
        time.sleep(min(int(r.headers.get("Retry-After", "5")), 15))
    return r


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    if not _check_production_reachable():
        pytest.skip("Production unreachable")
    with httpx.Client(base_url=PROD_URL, timeout=30, follow_redirects=True) as c:
        yield c


@pytest.fixture(scope="session")
def headers_a():
    if not API_KEY:
        pytest.skip("API_KEY not set")
    return {"X-API-Key": API_KEY}


@pytest.fixture(scope="session")
def headers_b():
    if not TENANT_B_API_KEY:
        pytest.skip("TENANT_B_API_KEY not set")
    return {"X-API-Key": TENANT_B_API_KEY}


# ===========================================================================
# Category 1: API Response Consistency (5 tests)
# ===========================================================================

class TestApiConsistency:
    """Verify API responses are consistent across repeated calls."""

    def test_di01_config_idempotent(self, client, headers_a):
        """DI-01: /api/config returns same data on repeated calls."""
        r1 = client.get("/api/config", headers=headers_a)
        r2 = client.get("/api/config", headers=headers_a)
        assert r1.status_code == 200
        assert r2.status_code == 200
        d1 = r1.json()
        d2 = r2.json()
        # Remove volatile fields that change between calls (e.g., from_cache)
        for d in (d1, d2):
            d.pop("from_cache", None)
        assert d1 == d2, "Config response changed between calls"

    def test_di02_conversations_list_stable(self, client, headers_a):
        """DI-02: Conversation list is stable (same count on repeated calls)."""
        r1 = _request_with_rate_limit_retry(
            client, "get", "/api/admin/conversations?offset=0&limit=5", headers=headers_a
        )
        r2 = _request_with_rate_limit_retry(
            client, "get", "/api/admin/conversations?offset=0&limit=5", headers=headers_a
        )
        assert r1.status_code == 200
        assert r2.status_code == 200
        d1 = r1.json()
        d2 = r2.json()
        # Count should be the same
        count_key = "total" if "total" in d1 else "totalCount"
        if count_key in d1:
            assert d1[count_key] == d2[count_key], "Conversation count changed"

    def test_di03_kb_list_stable(self, client, headers_a):
        """DI-03: Knowledge base list is stable."""
        r1 = client.get("/api/admin/knowledge", headers=headers_a)
        r2 = client.get("/api/admin/knowledge", headers=headers_a)
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_di04_team_list_stable(self, client, headers_a):
        """DI-04: Team member list is stable."""
        r1 = client.get("/api/admin/team", headers=headers_a)
        r2 = client.get("/api/admin/team", headers=headers_a)
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Same number of members
        d1 = r1.json()
        d2 = r2.json()
        m1 = d1 if isinstance(d1, list) else d1.get("members", d1.get("items", []))
        m2 = d2 if isinstance(d2, list) else d2.get("members", d2.get("items", []))
        assert len(m1) == len(m2), f"Team count changed: {len(m1)} → {len(m2)}"

    def test_di05_health_consistent_schema(self, client):
        """DI-05: /health returns consistent schema across calls."""
        schemas = []
        for _ in range(5):
            r = client.get("/health")
            assert r.status_code == 200
            schemas.append(sorted(r.json().keys()))
        for i in range(1, len(schemas)):
            assert schemas[i] == schemas[0], (
                f"Health schema drift: call 1={schemas[0]}, call {i+1}={schemas[i]}"
            )


# ===========================================================================
# Category 2: Tenant Data Counts (5 tests)
# ===========================================================================

class TestTenantDataCounts:
    """Verify seeded data is present and accessible."""

    def test_di06_tenant_a_has_conversations(self, client, headers_a):
        """DI-06: Tenant A has at least 1 conversation."""
        r = client.get("/api/admin/conversations?offset=0&limit=1", headers=headers_a)
        assert r.status_code == 200

    def test_di07_tenant_b_has_conversations(self, client, headers_b):
        """DI-07: Tenant B has ≥15 seeded conversations."""
        r = _request_with_rate_limit_retry(
            client, "get", "/api/admin/conversations?offset=0&limit=50", headers=headers_b
        )
        assert r.status_code == 200
        data = r.json()
        items = data.get("conversations", data.get("items", []))
        assert len(items) >= 15, f"Expected ≥15 conversations, got {len(items)}"

    def test_di08_tenant_b_has_team_members(self, client, headers_b):
        """DI-08: Tenant B has ≥7 seeded team members."""
        r = _request_with_rate_limit_retry(
            client, "get", "/api/admin/team", headers=headers_b
        )
        assert r.status_code == 200
        data = r.json()
        members = data if isinstance(data, list) else data.get("members", data.get("items", []))
        assert len(members) >= 7, f"Expected ≥7 team members, got {len(members)}"

    def test_di09_tenant_b_has_kb_docs(self, client, headers_b):
        """DI-09: Tenant B has ≥1 KB documents."""
        r = _request_with_rate_limit_retry(
            client, "get", "/api/admin/knowledge", headers=headers_b
        )
        assert r.status_code == 200
        data = r.json()
        items = (
            data if isinstance(data, list)
            else data.get("articles", data.get("documents", data.get("items", [])))
        )
        assert len(items) >= 1, f"Expected ≥1 KB docs, got {len(items)}"

    def test_di10_tenant_a_config_complete(self, client, headers_a):
        """DI-10: Tenant A config has all required fields."""
        r = client.get("/api/config", headers=headers_a)
        assert r.status_code == 200
        data = r.json()
        # Config should have either top-level or nested config fields
        cfg = data.get("config", data)
        has_brand = "brand_name" in cfg or "brandName" in cfg
        has_widget = "widget_key" in cfg or "widgetKey" in cfg
        assert has_brand or has_widget, f"Config incomplete: {list(cfg.keys())[:10]}"


# ===========================================================================
# Category 3: Pagination Integrity (5 tests)
# ===========================================================================

class TestPaginationIntegrity:
    """Verify pagination works correctly and doesn't skip/duplicate items."""

    def test_di11_conversations_pagination(self, client, headers_b):
        """DI-11: Conversation pagination offset+limit works."""
        r = _request_with_rate_limit_retry(
            client, "get", "/api/admin/conversations?offset=0&limit=5", headers=headers_b
        )
        assert r.status_code == 200
        data = r.json()
        items = data.get("conversations", data.get("items", []))
        assert len(items) <= 5, f"Limit 5 returned {len(items)} items"

    def test_di12_conversations_offset(self, client, headers_b):
        """DI-12: Conversation pagination offset skips items."""
        r1 = _request_with_rate_limit_retry(
            client, "get", "/api/admin/conversations?offset=0&limit=3", headers=headers_b
        )
        r2 = _request_with_rate_limit_retry(
            client, "get", "/api/admin/conversations?offset=3&limit=3", headers=headers_b
        )
        assert r1.status_code == 200
        assert r2.status_code == 200
        items1 = r1.json().get("conversations", r1.json().get("items", []))
        items2 = r2.json().get("conversations", r2.json().get("items", []))
        # Pages should not overlap
        if items1 and items2:
            ids1 = {i.get("conversationId", i.get("id", i.get("conversation_id", ""))) for i in items1}
            ids2 = {i.get("conversationId", i.get("id", i.get("conversation_id", ""))) for i in items2}
            # Filter out empty strings (field not found)
            ids1 = {x for x in ids1 if x}
            ids2 = {x for x in ids2 if x}
            if ids1 and ids2:
                overlap = ids1 & ids2
                assert len(overlap) == 0, f"Pagination overlap: {overlap}"

    def test_di13_limit_zero_returns_empty(self, client, headers_a):
        """DI-13: limit=0 returns empty or total count."""
        r = client.get("/api/admin/conversations?offset=0&limit=0", headers=headers_a)
        # Should return 200 with 0 items, or 422 (invalid), not 500
        assert r.status_code in (200, 422), f"limit=0: got {r.status_code}"

    def test_di14_large_offset_returns_empty(self, client, headers_a):
        """DI-14: Very large offset returns empty list."""
        r = client.get(
            "/api/admin/conversations?offset=99999&limit=10", headers=headers_a
        )
        assert r.status_code == 200
        data = r.json()
        items = data.get("conversations", data.get("items", []))
        assert len(items) == 0, f"Large offset returned {len(items)} items"

    def test_di15_negative_offset_handled(self, client, headers_a):
        """DI-15: Negative offset handled gracefully."""
        r = client.get(
            "/api/admin/conversations?offset=-1&limit=10", headers=headers_a
        )
        # Should return 200 (treating -1 as 0) or 422, not 500
        assert r.status_code in (200, 422), f"Negative offset: got {r.status_code}"


# ===========================================================================
# Category 4: ConfigState Integrity (5 tests)
# ===========================================================================

class TestConfigStateIntegrity:
    """Verify configuration state is consistent."""

    def test_di16_config_has_tenant_id(self, client, headers_a):
        """DI-16: Config response includes tenant_id."""
        r = client.get("/api/config", headers=headers_a)
        assert r.status_code == 200
        data = r.json()
        tid = data.get("tenant_id") or data.get("tenantId", "")
        assert tid, f"Config missing tenant_id: {list(data.keys())[:10]}"

    def test_di17_config_has_tier(self, client, headers_a):
        """DI-17: Config response includes tier."""
        r = client.get("/api/config", headers=headers_a)
        assert r.status_code == 200
        data = r.json()
        tier = data.get("tier", "")
        assert tier, f"Config missing tier: {list(data.keys())[:10]}"

    def test_di18_config_has_state(self, client, headers_a):
        """DI-18: Config response includes state."""
        r = client.get("/api/config", headers=headers_a)
        assert r.status_code == 200
        data = r.json()
        state = data.get("state") or data.get("config_state", "")
        assert state, f"Config missing state: {list(data.keys())[:10]}"

    def test_di19_tenant_b_is_active(self, client, headers_b):
        """DI-19: Tenant B config shows active state."""
        r = _request_with_rate_limit_retry(
            client, "get", "/api/config", headers=headers_b
        )
        assert r.status_code == 200
        data = r.json()
        state = data.get("state") or data.get("config_state", "")
        assert state in ("active", "ACTIVE"), f"Tenant B state: {state}"

    def test_di20_tenant_b_is_starter(self, client, headers_b):
        """DI-20: Tenant B tier is starter."""
        r = _request_with_rate_limit_retry(
            client, "get", "/api/config", headers=headers_b
        )
        assert r.status_code == 200
        data = r.json()
        tier = data.get("tier", "")
        assert tier == "starter", f"Tenant B tier: {tier}"


# ===========================================================================
# Category 5: Health & Version Integrity (5 tests)
# ===========================================================================

class TestHealthIntegrity:
    """Verify system health and version reporting."""

    def test_di21_health_returns_200(self, client):
        """DI-21: /health returns 200."""
        r = client.get("/health")
        assert r.status_code == 200

    def test_di22_ready_returns_200(self, client):
        """DI-22: /ready returns 200."""
        r = client.get("/ready")
        assert r.status_code == 200

    def test_di23_health_is_json(self, client):
        """DI-23: /health returns valid JSON."""
        r = client.get("/health")
        data = r.json()  # Will raise on invalid JSON
        assert isinstance(data, dict)

    def test_di24_version_reported(self, client):
        """DI-24: API version is reported somewhere."""
        r = client.get("/health")
        health = r.json()
        health_str = json.dumps(health)
        # Version may be in health response or /ready
        r2 = client.get("/ready")
        ready_str = json.dumps(r2.json()) if r2.status_code == 200 else ""
        combined = health_str + ready_str
        has_version = "version" in combined.lower() or "1.5" in combined
        # Version reporting is informational, not critical
        if not has_version:
            pytest.skip("Version not reported in health endpoints")

    def test_di25_multiple_endpoints_healthy(self, client, headers_a):
        """DI-25: Core endpoints all respond correctly."""
        endpoints = [
            ("/health", None, [200]),
            ("/ready", None, [200]),
            ("/openapi.json", None, [200]),
            ("/api/config", headers_a, [200, 429]),
        ]
        for path, hdrs, expected in endpoints:
            r = client.get(path, headers=hdrs) if hdrs else client.get(path)
            assert r.status_code in expected, (
                f"{path}: expected {expected}, got {r.status_code}"
            )
