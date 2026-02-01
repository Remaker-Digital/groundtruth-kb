"""Usage Dashboard API tests — HTTP endpoints for billing transparency (UD-01 to UD-15).

Tests UD-01 through UD-15 from COMPREHENSIVE-TEST-PLAN.md §5.10 (P1 pre-launch).

Validates:
    - GET /api/dashboard/usage (Layer 1 real-time)
    - GET /api/dashboard/usage/daily (daily volume chart data)
    - GET /api/dashboard/conversations (Layer 2 paginated list)
    - GET /api/dashboard/conversations/{id} (single conversation detail)
    - GET /api/dashboard/conversations/export (CSV export)
    - Service injection / 503 when unconfigured
    - Billing period validation
    - Tenant isolation (tenant_id from auth context only)

Work Items #73-74 (Decision #25).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantTier, TenantStatus
from src.multi_tenant.usage_dashboard_api import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationSummary,
    DailyVolumeEntry,
    DailyVolumeResponse,
    UsageDashboardResponse,
    configure_dashboard_services,
    router,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-dashboard-test-001"
BILLING_PERIOD = "2026-01"


# ---------------------------------------------------------------------------
# Mock usage dashboard data
# ---------------------------------------------------------------------------

@dataclass
class MockAlert:
    value: str


@dataclass
class MockUsageDashboard:
    tenant_id: str = TENANT_ID
    billing_period: str = BILLING_PERIOD
    total_conversations: int = 150
    included_allowance: int = 1000
    remaining_included: int = 850
    pack_balance: int = 200
    overage_conversations: int = 0
    overage_reported: int = 0
    usage_percent: float = 15.0
    estimated_overage_cost: float = 0.0
    active_alerts: list = field(default_factory=list)


MOCK_CONVERSATION_RAW = {
    "conversation_id": "conv-001",
    "status": "ended",
    "customer_id": "cust-001",
    "is_billable": True,
    "message_count": 8,
    "turn_count": 4,
    "started_at": "2026-01-15T10:30:00Z",
    "ended_at": "2026-01-15T10:35:00Z",
    "agents_invoked": ["intent-classifier", "response-generator"],
    "model_used": "gpt-4o",
    "critic_passed": True,
}

MOCK_CONVERSATION_DETAIL = {
    "conversation_id": "conv-001",
    "tenant_id": TENANT_ID,
    "status": "ended",
    "is_billable": True,
    "message_count": 8,
    "turn_count": 4,
    "started_at": "2026-01-15T10:30:00Z",
    "ended_at": "2026-01-15T10:35:00Z",
    "customer_id": "cust-001",
    "agents_invoked": ["intent-classifier", "response-generator"],
    "model_used": "gpt-4o",
    "critic_passed": True,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_tenant_context(tenant_id: str = TENANT_ID) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=TenantTier.STARTER,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


@pytest.fixture()
def mock_meter():
    meter = AsyncMock()
    meter.get_usage_dashboard = AsyncMock(return_value=MockUsageDashboard())
    meter.get_conversation_billing_detail = AsyncMock(return_value=MOCK_CONVERSATION_DETAIL)
    return meter


@pytest.fixture()
def mock_repo():
    repo = AsyncMock()
    repo.list_billable = AsyncMock(return_value=[MOCK_CONVERSATION_RAW])
    repo.count_billable = AsyncMock(return_value=1)
    repo.query = AsyncMock(return_value=[MOCK_CONVERSATION_RAW])
    return repo


@pytest.fixture()
def dashboard_client(mock_meter, mock_repo):
    """FastAPI test client with dashboard router and mocked services."""
    app = FastAPI()

    # Override tenant context dependency
    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()

    app.include_router(router)

    # Wire services
    configure_dashboard_services(mock_meter, mock_repo)

    client = TestClient(app)
    yield client

    # Cleanup: reset module-level services
    configure_dashboard_services(None, None)


@pytest.fixture()
def unconfigured_client():
    """Client where dashboard services are NOT configured — expect 503."""
    app = FastAPI()
    from src.multi_tenant.middleware import get_tenant_context
    app.dependency_overrides[get_tenant_context] = lambda: _make_tenant_context()
    app.include_router(router)

    # Ensure services are cleared
    configure_dashboard_services(None, None)

    client = TestClient(app)
    yield client


# ---------------------------------------------------------------------------
# Response model tests
# ---------------------------------------------------------------------------

class TestResponseModels:
    """Validate Pydantic response models."""

    def test_ud01_usage_dashboard_response_fields(self):
        """UD-01: UsageDashboardResponse has all required fields."""
        resp = UsageDashboardResponse(
            tenant_id=TENANT_ID,
            billing_period=BILLING_PERIOD,
            total_conversations=100,
            included_allowance=1000,
            remaining_included=900,
            pack_balance=50,
            overage_conversations=0,
            overage_reported=0,
            usage_percent=10.0,
            estimated_overage_cost=0.0,
            active_alerts=[],
        )
        assert resp.tenant_id == TENANT_ID
        assert resp.usage_percent == 10.0

    def test_ud02_daily_volume_entry(self):
        """UD-02: DailyVolumeEntry serializes correctly."""
        entry = DailyVolumeEntry(date="2026-01-15", total=20, billable=15)
        assert entry.date == "2026-01-15"
        assert entry.total == 20
        assert entry.billable == 15

    def test_ud03_conversation_summary(self):
        """UD-03: ConversationSummary defaults are correct."""
        summary = ConversationSummary(conversation_id="conv-001")
        assert summary.is_billable is False
        assert summary.message_count == 0
        assert summary.agents_invoked == []


# ---------------------------------------------------------------------------
# GET /api/dashboard/usage
# ---------------------------------------------------------------------------

class TestGetUsageDashboard:
    """Layer 1 real-time dashboard endpoint."""

    def test_ud04_get_usage_returns_dashboard(self, dashboard_client, mock_meter):
        """UD-04: GET /usage returns dashboard data."""
        resp = dashboard_client.get("/api/dashboard/usage")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == TENANT_ID
        assert data["total_conversations"] == 150
        assert data["included_allowance"] == 1000

    def test_ud05_usage_with_billing_period(self, dashboard_client, mock_meter):
        """UD-05: GET /usage accepts billing_period query param."""
        resp = dashboard_client.get("/api/dashboard/usage?billing_period=2026-01")
        assert resp.status_code == 200
        mock_meter.get_usage_dashboard.assert_called_once()
        call_kwargs = mock_meter.get_usage_dashboard.call_args[1]
        assert call_kwargs["billing_period"] == "2026-01"

    def test_ud06_usage_503_when_unconfigured(self, unconfigured_client):
        """UD-06: GET /usage returns 503 when services not initialized."""
        resp = unconfigured_client.get("/api/dashboard/usage")
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# GET /api/dashboard/usage/daily
# ---------------------------------------------------------------------------

class TestGetDailyVolume:
    """Daily volume chart data endpoint."""

    def test_ud07_daily_volume_returns_days(self, dashboard_client, mock_repo):
        """UD-07: GET /usage/daily returns per-day breakdown."""
        resp = dashboard_client.get("/api/dashboard/usage/daily?billing_period=2026-01")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == TENANT_ID
        assert data["billing_period"] == "2026-01"
        assert "days" in data

    def test_ud08_daily_volume_invalid_period(self, dashboard_client):
        """UD-08: GET /usage/daily rejects invalid billing_period format."""
        resp = dashboard_client.get("/api/dashboard/usage/daily?billing_period=invalid")
        assert resp.status_code == 422  # FastAPI validation (pattern mismatch)


# ---------------------------------------------------------------------------
# GET /api/dashboard/conversations
# ---------------------------------------------------------------------------

class TestListConversations:
    """Layer 2 paginated conversation list."""

    def test_ud09_list_conversations(self, dashboard_client, mock_repo):
        """UD-09: GET /conversations returns paginated list."""
        resp = dashboard_client.get("/api/dashboard/conversations?billing_period=2026-01")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == TENANT_ID
        assert "conversations" in data
        assert data["total_count"] == 1

    def test_ud10_list_conversations_pagination(self, dashboard_client, mock_repo):
        """UD-10: Pagination params are passed correctly."""
        resp = dashboard_client.get(
            "/api/dashboard/conversations?billing_period=2026-01&offset=10&limit=20"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["offset"] == 10
        assert data["limit"] == 20

    def test_ud11_list_conversations_limit_max(self, dashboard_client):
        """UD-11: Limit > 200 is rejected by validation."""
        resp = dashboard_client.get(
            "/api/dashboard/conversations?billing_period=2026-01&limit=300"
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/dashboard/conversations/{id}
# ---------------------------------------------------------------------------

class TestGetConversationDetail:
    """Single conversation billing detail."""

    def test_ud12_get_detail(self, dashboard_client, mock_meter):
        """UD-12: GET /conversations/{id} returns detail."""
        resp = dashboard_client.get("/api/dashboard/conversations/conv-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["conversation_id"] == "conv-001"
        assert data["is_billable"] is True

    def test_ud13_get_detail_not_found(self, dashboard_client, mock_meter):
        """UD-13: GET /conversations/{id} returns 404 on error."""
        mock_meter.get_conversation_billing_detail.side_effect = Exception("not found")
        resp = dashboard_client.get("/api/dashboard/conversations/missing-conv")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/conversations/export
# ---------------------------------------------------------------------------

class TestExportCSV:
    """CSV export endpoint."""

    def test_ud14_export_csv(self, dashboard_client, mock_repo):
        """UD-14: GET /conversations/export returns CSV."""
        resp = dashboard_client.get(
            "/api/dashboard/conversations/export?billing_period=2026-01"
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        assert "attachment" in resp.headers.get("content-disposition", "")

        # Verify CSV contains header and data row
        content = resp.text
        lines = content.strip().split("\n")
        assert len(lines) >= 2  # header + at least 1 data row
        assert "Conversation ID" in lines[0]

    def test_ud15_export_csv_503_unconfigured(self, unconfigured_client):
        """UD-15: CSV export returns 503 when services not initialized."""
        resp = unconfigured_client.get(
            "/api/dashboard/conversations/export?billing_period=2026-01"
        )
        assert resp.status_code == 503
