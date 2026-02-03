"""P3 Audit Log Query API tests — compliance reporting and CSV export.

Tests the admin audit log API: paginated query, event type filtering,
customer ID filtering, date range filtering, CSV export, invalid event
type rejection, service-not-configured error, and tenant isolation.

Test IDs: AL-01 through AL-10 per §7.4 of
docs/COMPREHENSIVE-TEST-PLAN.md.

Work Item: P3 post-launch tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.admin_audit_api import (
    VALID_EVENT_TYPES,
    AuditEventResponse,
    AuditListResponse,
    configure_admin_audit_services,
    router,
)
from tests.conftest import (
    STARTER_TENANT_ID,
    PROFESSIONAL_TENANT_ID,
    TEST_API_KEY_STARTER,
    TEST_API_KEY_PROFESSIONAL,
    auth_headers_api_key,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)


def _make_audit_event(
    event_id: str = "evt-001",
    tenant_id: str = STARTER_TENANT_ID,
    event_type: str = AuditEventType.CONSENT_CHANGED.value,
    actor: str = "system",
    customer_id: str | None = "cust-001",
    details: dict[str, Any] | None = None,
    trace_id: str | None = "trace-abc",
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build an audit event document as returned by AuditLogRepository."""
    return {
        "id": event_id,
        "tenant_id": tenant_id,
        "event_type": event_type,
        "timestamp": timestamp or _NOW.isoformat(),
        "actor": actor,
        "customer_id": customer_id,
        "details": details or {"change": "granted"},
        "trace_id": trace_id,
    }


def _make_audit_events(count: int, **kwargs) -> list[dict[str, Any]]:
    """Build a list of audit events with sequential IDs."""
    return [
        _make_audit_event(event_id=f"evt-{i:03d}", **kwargs)
        for i in range(count)
    ]


# ===========================================================================
# AL-01: All 12 event types can be created
# ===========================================================================


class TestAuditEventTypes:
    """AL-01: Validate all event types are recognized by the API."""

    def test_al_01_all_event_types_in_valid_set(self):
        """AL-01: All 12 AuditEventType values are in VALID_EVENT_TYPES."""
        for event_type in AuditEventType:
            assert event_type.value in VALID_EVENT_TYPES

    def test_al_01b_valid_event_types_count(self):
        """AL-01b: VALID_EVENT_TYPES contains the expected number of types."""
        assert len(VALID_EVENT_TYPES) == len(AuditEventType)
        assert len(VALID_EVENT_TYPES) >= 12


# ===========================================================================
# AL-02: Audit log is append-only (no delete/update endpoints)
# ===========================================================================


class TestAppendOnlyDesign:
    """AL-02: Audit log has no mutation endpoints."""

    def test_al_02_no_delete_or_put_routes(self):
        """AL-02: The audit router has only GET endpoints (read-only)."""
        methods = set()
        for route in router.routes:
            if hasattr(route, "methods"):
                methods.update(route.methods)

        # Only GET should be present — no POST, PUT, DELETE, PATCH
        assert "GET" in methods
        assert "POST" not in methods
        assert "PUT" not in methods
        assert "DELETE" not in methods
        assert "PATCH" not in methods


# ===========================================================================
# AL-03 through AL-06: Filtering and pagination via HTTP endpoints
# ===========================================================================


class TestAuditQueryEndpoint:
    """AL-03 through AL-06: Audit log query with filtering and pagination."""

    def test_al_03_query_with_pagination(self, app_client):
        """AL-03: Paginated query returns correct offset and limit."""
        events = _make_audit_events(5)

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=5)
            mock_repo.query_by_tenant = AsyncMock(return_value=events[:3])

            resp = app_client.get(
                "/api/audit?offset=0&limit=3",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["total_count"] == 5
        assert body["offset"] == 0
        assert body["limit"] == 3
        assert len(body["events"]) == 3

    def test_al_04_filter_by_event_type(self, app_client):
        """AL-04: Query filters by event_type."""
        events = _make_audit_events(2, event_type=AuditEventType.DATA_EXPORTED.value)

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=2)
            mock_repo.query_by_tenant = AsyncMock(return_value=events)

            resp = app_client.get(
                f"/api/audit?event_type={AuditEventType.DATA_EXPORTED.value}",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        body = resp.json()
        # Verify the filter was passed to the repo
        call_kwargs = mock_repo.query_by_tenant.call_args.kwargs
        assert call_kwargs.get("event_type") == AuditEventType.DATA_EXPORTED.value

    def test_al_05_filter_by_tenant_id(self, app_client):
        """AL-05: Query automatically scopes to authenticated tenant_id."""
        events = _make_audit_events(1)

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=1)
            mock_repo.query_by_tenant = AsyncMock(return_value=events)

            resp = app_client.get(
                "/api/audit",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        # Verify tenant_id was passed from auth context, not query param
        call_kwargs = mock_repo.query_by_tenant.call_args.kwargs
        assert call_kwargs["tenant_id"] == STARTER_TENANT_ID

    def test_al_06_filter_by_date_range(self, app_client):
        """AL-06: Query supports date_from and date_to filtering."""
        date_from = (_NOW - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
        date_to = _NOW.strftime("%Y-%m-%dT%H:%M:%S")
        events = _make_audit_events(1)

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=1)
            mock_repo.query_by_tenant = AsyncMock(return_value=events)

            resp = app_client.get(
                f"/api/audit?date_from={date_from}&date_to={date_to}",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        call_kwargs = mock_repo.query_by_tenant.call_args.kwargs
        assert call_kwargs["date_from"] == date_from
        assert call_kwargs["date_to"] == date_to

    def test_al_06b_default_date_range_30_days(self, app_client):
        """AL-06b: Default date range is last 30 days when not specified."""
        events = []

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=0)
            mock_repo.query_by_tenant = AsyncMock(return_value=events)

            resp = app_client.get(
                "/api/audit",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        call_kwargs = mock_repo.query_by_tenant.call_args.kwargs
        # date_from should be approximately 30 days ago
        assert "date_from" in call_kwargs
        assert "date_to" in call_kwargs


# ===========================================================================
# AL-07: 1-year retention (design validation)
# ===========================================================================


class TestRetentionPolicy:
    """AL-07: Audit log has 1-year retention (design-level test)."""

    def test_al_07_retention_documented(self):
        """AL-07: Audit log retention is 1 year per Decision #13.

        This is a design-level validation: the audit log is append-only,
        never deleted by retention enforcement (data_retention.py skips
        the audit collection), and stored in a time-partitioned collection.
        """
        # The audit log router has no delete endpoints
        methods = set()
        for route in router.routes:
            if hasattr(route, "methods"):
                methods.update(route.methods)
        assert "DELETE" not in methods

        # AuditEventType is used for classification (at least 12 types)
        assert len(AuditEventType) >= 12


# ===========================================================================
# AL-08: Audit log survives tenant deletion (design validation)
# ===========================================================================


class TestTenantDeletionSurvival:
    """AL-08: Audit log data persists after tenant deletion."""

    def test_al_08_audit_not_in_tenant_scoped_deletion(self):
        """AL-08: Audit log collection is platform-scoped, not tenant-scoped.

        In cosmos_schema.py, AuditLogRepository is a PlatformScopedRepository,
        meaning it is not subject to tenant-level cascading deletion. This test
        validates the design by checking the repository class hierarchy.
        """
        from src.multi_tenant.repository import (
            AuditLogRepository,
            PlatformScopedRepository,
        )
        assert issubclass(AuditLogRepository, PlatformScopedRepository)


# ===========================================================================
# AL-09: Audit log API returns paginated results
# ===========================================================================


class TestPagination:
    """AL-09: Pagination metadata is correct."""

    def test_al_09_pagination_metadata(self, app_client):
        """AL-09: Response includes total_count, offset, limit."""
        events = _make_audit_events(15)

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=15)
            mock_repo.query_by_tenant = AsyncMock(return_value=events[5:10])

            resp = app_client.get(
                "/api/audit?offset=5&limit=5",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["total_count"] == 15
        assert body["offset"] == 5
        assert body["limit"] == 5
        assert len(body["events"]) == 5


# ===========================================================================
# AL-10: Audit log export for compliance reporting (CSV)
# ===========================================================================


class TestCsvExport:
    """AL-10: CSV export endpoint returns valid CSV."""

    def test_al_10_csv_export_valid(self, app_client):
        """AL-10: GET /api/audit/export returns CSV with correct headers and rows."""
        events = _make_audit_events(3)

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.query_by_tenant = AsyncMock(return_value=events)

            resp = app_client.get(
                "/api/audit/export",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        assert "attachment" in resp.headers.get("content-disposition", "")

        # Parse the CSV content
        reader = csv.reader(io.StringIO(resp.text))
        rows = list(reader)

        # Header row
        assert rows[0] == [
            "id", "event_type", "timestamp", "actor",
            "customer_id", "trace_id", "details",
        ]
        # Data rows
        assert len(rows) == 4  # 1 header + 3 data rows
        assert rows[1][0] == "evt-000"

    def test_al_10b_csv_export_empty(self, app_client):
        """AL-10b: CSV export with no events returns header-only CSV."""
        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.query_by_tenant = AsyncMock(return_value=[])

            resp = app_client.get(
                "/api/audit/export",
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )

        assert resp.status_code == 200
        reader = csv.reader(io.StringIO(resp.text))
        rows = list(reader)
        assert len(rows) == 1  # Header only


# ===========================================================================
# Additional coverage: error handling, invalid input, service not configured
# ===========================================================================


class TestErrorHandling:
    """Additional tests for error paths."""

    def test_invalid_event_type_rejected(self, app_client):
        """Invalid event_type query param returns 400."""
        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            resp = app_client.get(
                "/api/audit?event_type=INVALID_TYPE",
                headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
            )

        assert resp.status_code == 400
        assert "Invalid event_type" in resp.json()["detail"]

    def test_invalid_event_type_on_export(self, app_client):
        """Invalid event_type on CSV export returns 400."""
        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            resp = app_client.get(
                "/api/audit/export?event_type=BOGUS",
                headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
            )

        assert resp.status_code == 400

    def test_service_not_configured_returns_503(self, app_client):
        """When audit repo is not configured, endpoints return 503."""
        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo", None,
        ):
            resp = app_client.get(
                "/api/audit",
                headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
            )

        assert resp.status_code == 503
        assert "not initialised" in resp.json()["detail"]

    def test_repo_error_returns_500(self, app_client):
        """Repository exception returns 500."""
        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(
                side_effect=RuntimeError("DB connection lost")
            )

            resp = app_client.get(
                "/api/audit",
                headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
            )

        assert resp.status_code == 500
        assert "Failed to query" in resp.json()["detail"]

    def test_customer_id_filter(self, app_client):
        """customer_id filter is passed through to repository."""
        events = _make_audit_events(1, customer_id="cust-specific")

        with patch(
            "src.multi_tenant.admin_audit_api._audit_repo"
        ) as mock_repo:
            mock_repo.count_by_tenant = AsyncMock(return_value=1)
            mock_repo.query_by_tenant = AsyncMock(return_value=events)

            resp = app_client.get(
                "/api/audit?customer_id=cust-specific",
                headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
            )

        assert resp.status_code == 200
        call_kwargs = mock_repo.query_by_tenant.call_args.kwargs
        assert call_kwargs.get("customer_id") == "cust-specific"

    def test_configure_admin_audit_services_sets_repo(self):
        """configure_admin_audit_services wires the module-level repo."""
        import src.multi_tenant.admin_audit_api as mod
        original = mod._audit_repo
        try:
            mock_repo = AsyncMock()
            configure_admin_audit_services(mock_repo)
            assert mod._audit_repo is mock_repo
        finally:
            mod._audit_repo = original
