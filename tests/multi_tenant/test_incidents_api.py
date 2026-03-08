"""Tests for HV-5: Incident Management endpoints + Public Status API.

Covers:
    Incident CRUD (superadmin):
    - List incidents (empty, multiple, with limit)
    - Create incident (happy path, missing fields, severity extraction)
    - Get single incident (found, not found)
    - Add status update (happy path, incident not found, update returns None)
    - Resolve incident (happy path, already resolved, not found)
    - Service not configured → 503

    Public Status API (no auth):
    - No active incidents → operational
    - Active incidents → correct severity mapping
    - Mixed severity → overall_status reflects worst
    - Incident repo not configured → graceful degradation
    - Last update populated from updates list

    Serialization:
    - CamelCase alias generation on response models

    Auth enforcement:
    - CRUD endpoints require SUPERADMIN via Depends
    - Public status has no auth dependency

Total: 32 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.multi_tenant.superadmin_api import (
    AddIncidentUpdateRequest,
    CreateIncidentRequest,
    IncidentListResponse,
    IncidentModel,
    IncidentUpdateModel,
    configure_superadmin_services,
)
from src.multi_tenant.status_api import (
    ActiveIncidentPublic,
    PublicStatusResponse,
    configure_status_api,
)


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------


def _make_incident_doc(
    incident_id: str = "inc-abc123",
    title: str = "API Degradation",
    description: str = "Elevated error rates on API endpoints",
    status: str = "investigating",
    severity: str = "major",
    affected_services: list[str] | None = None,
    updates: list[dict[str, str]] | None = None,
    created_by: str = "admin@remaker.com",
    resolved_at: str | None = None,
) -> dict[str, Any]:
    """Build a mock incident Cosmos document."""
    if affected_services is None:
        affected_services = ["API"]
    if updates is None:
        updates = [
            {
                "timestamp": "2026-02-17T10:00:00+00:00",
                "status": "investigating",
                "message": f"Incident created: {title}",
                "author": created_by,
            },
        ]
    return {
        "id": incident_id,
        "incident_id": incident_id,
        "title": title,
        "description": description,
        "status": status,
        "severity": severity,
        "affected_services": affected_services,
        "updates": updates,
        "created_at": "2026-02-17T10:00:00+00:00",
        "updated_at": "2026-02-17T10:00:00+00:00",
        "resolved_at": resolved_at,
        "created_by": created_by,
    }


INCIDENT_A = _make_incident_doc(
    incident_id="inc-aaa111",
    title="API Degradation",
    severity="major",
    affected_services=["API"],
)

INCIDENT_B = _make_incident_doc(
    incident_id="inc-bbb222",
    title="Widget Timeout",
    severity="critical",
    affected_services=["Widget", "NATS"],
    status="identified",
    updates=[
        {
            "timestamp": "2026-02-17T09:00:00+00:00",
            "status": "investigating",
            "message": "Incident created: Widget Timeout",
            "author": "admin@remaker.com",
        },
        {
            "timestamp": "2026-02-17T09:30:00+00:00",
            "status": "identified",
            "message": "Root cause identified: NATS backpressure",
            "author": "admin@remaker.com",
        },
    ],
)

INCIDENT_RESOLVED = _make_incident_doc(
    incident_id="inc-ccc333",
    title="Cosmos Latency Spike",
    severity="minor",
    status="resolved",
    affected_services=["Cosmos DB"],
    resolved_at="2026-02-17T12:00:00+00:00",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_incident_repo():
    """Create a mock IncidentRepository."""
    repo = MagicMock()
    repo.list_all = AsyncMock(return_value=[])
    repo.list_active = AsyncMock(return_value=[])
    repo.create_incident = AsyncMock()
    repo.find_incident = AsyncMock(return_value=None)
    repo.add_update = AsyncMock(return_value=None)
    repo.resolve_incident = AsyncMock(return_value=None)
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Create a fake SUPERADMIN TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    ctx.team_member_email = "admin@remaker.com"
    return ctx


@pytest.fixture(autouse=True)
def _wire_services(mock_incident_repo):
    """Wire mock incident repo into superadmin API for every test."""
    configure_superadmin_services(
        tenant_repo=MagicMock(),
        audit_repo=MagicMock(),
        incident_repo=mock_incident_repo,
    )
    configure_status_api(incident_repo=mock_incident_repo)
    yield


# ---------------------------------------------------------------------------
# List Incidents
# ---------------------------------------------------------------------------


class TestListIncidents:
    """Tests for GET /api/superadmin/incidents."""

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_incident_repo, superadmin_ctx):
        """Returns empty list when no incidents exist."""
        mock_incident_repo.list_all.return_value = []

        from src.multi_tenant.superadmin_api import list_incidents

        result = await list_incidents()

        assert isinstance(result, IncidentListResponse)
        assert result.total == 0
        assert result.incidents == []

    @pytest.mark.asyncio
    async def test_list_multiple(self, mock_incident_repo, superadmin_ctx):
        """Returns all incidents from repository."""
        mock_incident_repo.list_all.return_value = [INCIDENT_A, INCIDENT_B]

        from src.multi_tenant.superadmin_api import list_incidents

        result = await list_incidents()

        assert result.total == 2
        assert len(result.incidents) == 2
        assert result.incidents[0].incident_id == "inc-aaa111"
        assert result.incidents[1].incident_id == "inc-bbb222"

    @pytest.mark.asyncio
    async def test_list_passes_limit(self, mock_incident_repo, superadmin_ctx):
        """Limit parameter is forwarded to repository."""
        mock_incident_repo.list_all.return_value = [INCIDENT_A]

        from src.multi_tenant.superadmin_api import list_incidents

        await list_incidents(limit=10)

        mock_incident_repo.list_all.assert_awaited_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_list_service_not_configured(self, superadmin_ctx):
        """Returns 503 when incident repo is not configured."""
        configure_superadmin_services(
            tenant_repo=MagicMock(),
            audit_repo=MagicMock(),
            incident_repo=None,
        )

        from src.multi_tenant.superadmin_api import list_incidents

        with pytest.raises(HTTPException) as exc_info:
            await list_incidents()
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Create Incident
# ---------------------------------------------------------------------------


class TestCreateIncident:
    """Tests for POST /api/superadmin/incidents."""

    @pytest.mark.asyncio
    async def test_create_happy_path(self, mock_incident_repo, superadmin_ctx):
        """Creates incident and returns the model."""
        mock_incident_repo.create_incident.return_value = INCIDENT_A

        from src.multi_tenant.superadmin_api import create_incident

        body = CreateIncidentRequest(
            title="API Degradation",
            description="Elevated error rates",
            severity="major",
            affected_services=["API"],
        )
        result = await create_incident(body=body, ctx=superadmin_ctx)

        assert isinstance(result, IncidentModel)
        assert result.incident_id == "inc-aaa111"
        assert result.title == "API Degradation"
        assert result.severity == "major"

    @pytest.mark.asyncio
    async def test_create_passes_created_by(self, mock_incident_repo, superadmin_ctx):
        """created_by is extracted from team member email."""
        mock_incident_repo.create_incident.return_value = INCIDENT_A

        from src.multi_tenant.superadmin_api import create_incident

        body = CreateIncidentRequest(title="Test", severity="minor")
        await create_incident(body=body, ctx=superadmin_ctx)

        call_kwargs = mock_incident_repo.create_incident.call_args.kwargs
        assert call_kwargs["created_by"] == "admin@remaker.com"

    @pytest.mark.asyncio
    async def test_create_default_severity(self, mock_incident_repo, superadmin_ctx):
        """Severity defaults to 'minor' when not specified."""
        mock_incident_repo.create_incident.return_value = _make_incident_doc(
            severity="minor",
        )

        from src.multi_tenant.superadmin_api import create_incident

        body = CreateIncidentRequest(title="Test Incident")
        await create_incident(body=body, ctx=superadmin_ctx)

        call_kwargs = mock_incident_repo.create_incident.call_args.kwargs
        assert call_kwargs["severity"] == "minor"

    @pytest.mark.asyncio
    async def test_create_with_affected_services(self, mock_incident_repo, superadmin_ctx):
        """affected_services list is passed through."""
        mock_incident_repo.create_incident.return_value = INCIDENT_B

        from src.multi_tenant.superadmin_api import create_incident

        body = CreateIncidentRequest(
            title="Widget Timeout",
            severity="critical",
            affected_services=["Widget", "NATS"],
        )
        await create_incident(body=body, ctx=superadmin_ctx)

        call_kwargs = mock_incident_repo.create_incident.call_args.kwargs
        assert call_kwargs["affected_services"] == ["Widget", "NATS"]

    @pytest.mark.asyncio
    async def test_create_service_not_configured(self, superadmin_ctx):
        """Returns 503 when incident repo is not configured."""
        configure_superadmin_services(
            tenant_repo=MagicMock(),
            audit_repo=MagicMock(),
            incident_repo=None,
        )

        from src.multi_tenant.superadmin_api import create_incident

        body = CreateIncidentRequest(title="Test")
        with pytest.raises(HTTPException) as exc_info:
            await create_incident(body=body, ctx=superadmin_ctx)
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Get Single Incident
# ---------------------------------------------------------------------------


class TestGetIncident:
    """Tests for GET /api/superadmin/incidents/{incident_id}."""

    @pytest.mark.asyncio
    async def test_get_found(self, mock_incident_repo, superadmin_ctx):
        """Returns incident when found."""
        mock_incident_repo.find_incident.return_value = INCIDENT_A

        from src.multi_tenant.superadmin_api import get_incident

        result = await get_incident(incident_id="inc-aaa111")

        assert isinstance(result, IncidentModel)
        assert result.incident_id == "inc-aaa111"
        assert result.status == "investigating"

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_incident_repo, superadmin_ctx):
        """Returns 404 when incident does not exist."""
        mock_incident_repo.find_incident.return_value = None

        from src.multi_tenant.superadmin_api import get_incident

        with pytest.raises(HTTPException) as exc_info:
            await get_incident(incident_id="inc-nonexistent")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_populates_updates(self, mock_incident_repo, superadmin_ctx):
        """Updates list is correctly mapped to IncidentUpdateModel."""
        mock_incident_repo.find_incident.return_value = INCIDENT_B

        from src.multi_tenant.superadmin_api import get_incident

        result = await get_incident(incident_id="inc-bbb222")

        assert len(result.updates) == 2
        assert result.updates[0].status == "investigating"
        assert result.updates[1].status == "identified"
        assert result.updates[1].message == "Root cause identified: NATS backpressure"


# ---------------------------------------------------------------------------
# Add Status Update
# ---------------------------------------------------------------------------


class TestAddIncidentUpdate:
    """Tests for POST /api/superadmin/incidents/{incident_id}/update."""

    @pytest.mark.asyncio
    async def test_update_happy_path(self, mock_incident_repo, superadmin_ctx):
        """Adds update and returns modified incident."""
        mock_incident_repo.find_incident.return_value = INCIDENT_A
        updated_doc = {**INCIDENT_A, "status": "identified"}
        mock_incident_repo.add_update.return_value = updated_doc

        from src.multi_tenant.superadmin_api import add_incident_update

        body = AddIncidentUpdateRequest(
            status="identified",
            message="Root cause found",
        )
        result = await add_incident_update(
            incident_id="inc-aaa111",
            body=body,
            ctx=superadmin_ctx,
        )

        assert isinstance(result, IncidentModel)
        mock_incident_repo.add_update.assert_awaited_once()
        call_kwargs = mock_incident_repo.add_update.call_args.kwargs
        assert call_kwargs["new_status"] == "identified"
        assert call_kwargs["message"] == "Root cause found"
        assert call_kwargs["author"] == "admin@remaker.com"

    @pytest.mark.asyncio
    async def test_update_incident_not_found(self, mock_incident_repo, superadmin_ctx):
        """Returns 404 when incident does not exist."""
        mock_incident_repo.find_incident.return_value = None

        from src.multi_tenant.superadmin_api import add_incident_update

        body = AddIncidentUpdateRequest(status="identified", message="test")
        with pytest.raises(HTTPException) as exc_info:
            await add_incident_update(
                incident_id="inc-nonexistent",
                body=body,
                ctx=superadmin_ctx,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_returns_500_on_repo_failure(
        self, mock_incident_repo, superadmin_ctx
    ):
        """Returns 500 when repo add_update returns None."""
        mock_incident_repo.find_incident.return_value = INCIDENT_A
        mock_incident_repo.add_update.return_value = None

        from src.multi_tenant.superadmin_api import add_incident_update

        body = AddIncidentUpdateRequest(status="identified", message="test")
        with pytest.raises(HTTPException) as exc_info:
            await add_incident_update(
                incident_id="inc-aaa111",
                body=body,
                ctx=superadmin_ctx,
            )
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_update_passes_current_status(
        self, mock_incident_repo, superadmin_ctx
    ):
        """current_status is read from existing document."""
        mock_incident_repo.find_incident.return_value = INCIDENT_B
        mock_incident_repo.add_update.return_value = INCIDENT_B

        from src.multi_tenant.superadmin_api import add_incident_update

        body = AddIncidentUpdateRequest(status="monitoring", message="watching")
        await add_incident_update(
            incident_id="inc-bbb222",
            body=body,
            ctx=superadmin_ctx,
        )

        call_kwargs = mock_incident_repo.add_update.call_args.kwargs
        assert call_kwargs["current_status"] == "identified"


# ---------------------------------------------------------------------------
# Resolve Incident
# ---------------------------------------------------------------------------


class TestResolveIncident:
    """Tests for POST /api/superadmin/incidents/{incident_id}/resolve."""

    @pytest.mark.asyncio
    async def test_resolve_happy_path(self, mock_incident_repo, superadmin_ctx):
        """Resolves an active incident."""
        mock_incident_repo.find_incident.return_value = INCIDENT_A
        mock_incident_repo.resolve_incident.return_value = {
            **INCIDENT_A,
            "status": "resolved",
            "resolved_at": "2026-02-17T12:00:00+00:00",
        }

        from src.multi_tenant.superadmin_api import resolve_incident

        result = await resolve_incident(
            incident_id="inc-aaa111",
            message="All clear",
            ctx=superadmin_ctx,
        )

        assert isinstance(result, IncidentModel)
        mock_incident_repo.resolve_incident.assert_awaited_once()
        call_kwargs = mock_incident_repo.resolve_incident.call_args.kwargs
        assert call_kwargs["message"] == "All clear"
        assert call_kwargs["author"] == "admin@remaker.com"

    @pytest.mark.asyncio
    async def test_resolve_not_found(self, mock_incident_repo, superadmin_ctx):
        """Returns 404 when incident does not exist."""
        mock_incident_repo.find_incident.return_value = None

        from src.multi_tenant.superadmin_api import resolve_incident

        with pytest.raises(HTTPException) as exc_info:
            await resolve_incident(
                incident_id="inc-nonexistent",
                ctx=superadmin_ctx,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_resolve_already_resolved(self, mock_incident_repo, superadmin_ctx):
        """Returns 400 when incident is already resolved."""
        mock_incident_repo.find_incident.return_value = INCIDENT_RESOLVED

        from src.multi_tenant.superadmin_api import resolve_incident

        with pytest.raises(HTTPException) as exc_info:
            await resolve_incident(
                incident_id="inc-ccc333",
                ctx=superadmin_ctx,
            )
        assert exc_info.value.status_code == 400
        assert "already resolved" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_resolve_returns_500_on_repo_failure(
        self, mock_incident_repo, superadmin_ctx
    ):
        """Returns 500 when repo resolve returns None."""
        mock_incident_repo.find_incident.return_value = INCIDENT_A
        mock_incident_repo.resolve_incident.return_value = None

        from src.multi_tenant.superadmin_api import resolve_incident

        with pytest.raises(HTTPException) as exc_info:
            await resolve_incident(
                incident_id="inc-aaa111",
                ctx=superadmin_ctx,
            )
        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# Public Status API
# ---------------------------------------------------------------------------


class TestPublicStatus:
    """Tests for GET /api/status (no auth)."""

    @pytest.mark.asyncio
    async def test_no_active_incidents(self, mock_incident_repo):
        """Returns operational when no active incidents."""
        mock_incident_repo.list_active.return_value = []

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        assert isinstance(result, PublicStatusResponse)
        assert result.overall_status == "operational"
        assert result.active_incidents == []

    @pytest.mark.asyncio
    async def test_critical_incident_major_outage(self, mock_incident_repo):
        """Critical incident on a known service produces major_outage."""
        mock_incident_repo.list_active.return_value = [INCIDENT_B]

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        assert result.overall_status == "major_outage"
        assert len(result.active_incidents) == 1
        assert result.active_incidents[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_major_incident_partial_outage(self, mock_incident_repo):
        """Major incident produces partial_outage."""
        mock_incident_repo.list_active.return_value = [INCIDENT_A]

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        assert result.overall_status == "partial_outage"

    @pytest.mark.asyncio
    async def test_minor_incident_degraded(self, mock_incident_repo):
        """Minor incident produces degraded status."""
        minor_incident = _make_incident_doc(
            incident_id="inc-ddd444",
            title="Slow responses",
            severity="minor",
            affected_services=["API"],
        )
        mock_incident_repo.list_active.return_value = [minor_incident]

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        assert result.overall_status == "degraded"

    @pytest.mark.asyncio
    async def test_mixed_severity_worst_wins(self, mock_incident_repo):
        """Overall status reflects the worst severity across incidents."""
        minor_doc = _make_incident_doc(
            incident_id="inc-ddd444",
            severity="minor",
            affected_services=["Cosmos DB"],
        )
        mock_incident_repo.list_active.return_value = [minor_doc, INCIDENT_B]

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        assert result.overall_status == "major_outage"

    @pytest.mark.asyncio
    async def test_last_update_populated(self, mock_incident_repo):
        """Last update is taken from the final entry in the updates list."""
        mock_incident_repo.list_active.return_value = [INCIDENT_B]

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        last_upd = result.active_incidents[0].last_update
        assert last_upd is not None
        assert last_upd.status == "identified"
        assert "NATS backpressure" in last_upd.message

    @pytest.mark.asyncio
    async def test_repo_not_configured_graceful(self):
        """Returns operational when repo is None (graceful degradation)."""
        configure_status_api(incident_repo=None)

        from src.multi_tenant.status_api import public_status

        result = await public_status()

        assert result.overall_status == "operational"
        assert result.active_incidents == []

    @pytest.mark.asyncio
    async def test_services_list_populated(self, mock_incident_repo):
        """Services list contains all INCIDENT_SERVICES entries."""
        mock_incident_repo.list_active.return_value = []

        from src.multi_tenant.cosmos_schema import INCIDENT_SERVICES
        from src.multi_tenant.status_api import public_status

        result = await public_status()

        service_names = [s["name"] for s in result.services]
        for svc in INCIDENT_SERVICES:
            assert svc in service_names


# ---------------------------------------------------------------------------
# CamelCase Serialization
# ---------------------------------------------------------------------------


class TestIncidentSerialization:
    """CamelCase serialization and model correctness."""

    def test_incident_model_camel_case(self):
        """IncidentModel serializes field names to camelCase."""
        model = IncidentModel(
            incident_id="inc-test",
            title="Test",
            status="investigating",
            severity="minor",
            affected_services=["API"],
            created_at="2026-02-17T10:00:00+00:00",
            updated_at="2026-02-17T10:00:00+00:00",
            created_by="admin@remaker.com",
        )
        data = model.model_dump(by_alias=True)

        assert "incidentId" in data
        assert "affectedServices" in data
        assert "createdAt" in data
        assert "updatedAt" in data
        assert "resolvedAt" in data
        assert "createdBy" in data
        assert data["incidentId"] == "inc-test"

    def test_incident_list_response_camel_case(self):
        """IncidentListResponse serializes correctly."""
        resp = IncidentListResponse(
            incidents=[],
            total=0,
        )
        data = resp.model_dump(by_alias=True)
        assert "incidents" in data
        assert "total" in data

    def test_incident_update_model_camel_case(self):
        """IncidentUpdateModel serializes correctly."""
        update = IncidentUpdateModel(
            timestamp="2026-02-17T10:00:00+00:00",
            status="investigating",
            message="Looking into it",
            author="admin@remaker.com",
        )
        data = update.model_dump(by_alias=True)
        assert "timestamp" in data
        assert "status" in data
        assert "message" in data
        assert "author" in data

    def test_public_status_response_camel_case(self):
        """PublicStatusResponse serializes to camelCase."""
        resp = PublicStatusResponse(
            overall_status="operational",
            active_incidents=[],
        )
        data = resp.model_dump(by_alias=True)

        assert "overallStatus" in data
        assert "activeIncidents" in data
        assert data["overallStatus"] == "operational"


# ---------------------------------------------------------------------------
# Auth Enforcement
# ---------------------------------------------------------------------------


class TestIncidentAuth:
    """Auth dependency verification."""

    def test_list_requires_platform_admin(self):
        """SPEC-1667: list_incidents protected by router-level require_platform_admin()."""
        from src.multi_tenant.superadmin_api import router

        assert len(router.dependencies) > 0, (
            "Router must have require_platform_admin() as a dependency"
        )

    @pytest.mark.asyncio
    async def test_create_requires_superadmin(self):
        """create_incident depends on require_role(SUPERADMIN)."""
        import inspect

        from src.multi_tenant.superadmin_api import create_incident

        sig = inspect.signature(create_incident)
        ctx_param = sig.parameters.get("ctx")
        assert ctx_param is not None
        assert ctx_param.default is not inspect.Parameter.empty

    @pytest.mark.asyncio
    async def test_resolve_requires_superadmin(self):
        """resolve_incident depends on require_role(SUPERADMIN)."""
        import inspect

        from src.multi_tenant.superadmin_api import resolve_incident

        sig = inspect.signature(resolve_incident)
        ctx_param = sig.parameters.get("ctx")
        assert ctx_param is not None
        assert ctx_param.default is not inspect.Parameter.empty

    def test_public_status_no_auth(self):
        """public_status has no auth dependency parameter."""
        import inspect

        from src.multi_tenant.status_api import public_status

        sig = inspect.signature(public_status)
        for param in sig.parameters.values():
            assert "TenantContext" not in str(param.annotation)

    def test_incident_routes_under_superadmin(self):
        """Incident endpoints are mounted under /api/superadmin."""
        from src.multi_tenant.superadmin_api import router

        routes = [r.path for r in router.routes]
        assert "/api/superadmin/incidents" in routes
        assert "/api/superadmin/incidents/{incident_id}" in routes
        assert "/api/superadmin/incidents/{incident_id}/update" in routes
        assert "/api/superadmin/incidents/{incident_id}/resolve" in routes

    def test_status_route_is_public(self):
        """Public status is mounted at /api/status (no /superadmin prefix)."""
        from src.multi_tenant.status_api import router

        routes = [r.path for r in router.routes]
        assert "/api/status" in routes
