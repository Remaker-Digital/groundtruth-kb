# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Public Status API — unauthenticated service status endpoint.

Returns current platform status and active incidents for public
consumption (status pages, monitoring dashboards).

No authentication required. Read-only.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["status"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class IncidentUpdatePublic(CamelCaseModel):
    """A single update on an incident (public view)."""

    timestamp: str
    status: str
    message: str


class ActiveIncidentPublic(CamelCaseModel):
    """Minimal incident data for public status page."""

    incident_id: str
    title: str
    status: str
    severity: str
    affected_services: list[str] = Field(default_factory=list)
    created_at: str
    last_update: IncidentUpdatePublic | None = None


class PublicStatusResponse(CamelCaseModel):
    """Public platform status response."""

    overall_status: str = "operational"
    active_incidents: list[ActiveIncidentPublic] = Field(default_factory=list)
    services: list[dict[str, str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Module-level service reference
# ---------------------------------------------------------------------------

_incident_repo: Any = None


def configure_status_api(incident_repo: Any) -> None:
    """Wire the IncidentRepository into the status API."""
    global _incident_repo
    _incident_repo = incident_repo
    logger.info("Public status API configured")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/api/status",
    response_model=PublicStatusResponse,
    summary="Public platform status",
    description=(
        "Returns current platform status and active incidents. "
        "No authentication required."
    ),
    status_code=200,
)
async def public_status() -> PublicStatusResponse:
    """Get current platform status and active incidents."""
    from src.multi_tenant.cosmos_schema import INCIDENT_SERVICES

    services = [{"name": svc, "status": "operational"} for svc in INCIDENT_SERVICES]
    active_incidents: list[ActiveIncidentPublic] = []

    if _incident_repo is not None:
        try:
            incidents = await _incident_repo.list_active()
            for inc in incidents:
                last_update = None
                updates = inc.get("updates", [])
                if updates:
                    last = updates[-1]
                    last_update = IncidentUpdatePublic(
                        timestamp=last.get("timestamp", ""),
                        status=last.get("status", ""),
                        message=last.get("message", ""),
                    )

                active_incidents.append(ActiveIncidentPublic(
                    incident_id=inc.get("incident_id", ""),
                    title=inc.get("title", ""),
                    status=inc.get("status", "investigating"),
                    severity=inc.get("severity", "minor"),
                    affected_services=inc.get("affected_services", []),
                    created_at=inc.get("created_at", ""),
                    last_update=last_update,
                ))

                # Mark affected services
                for affected in inc.get("affected_services", []):
                    for svc in services:
                        if svc["name"] == affected:
                            severity = inc.get("severity", "minor")
                            if severity == "critical":
                                svc["status"] = "major_outage"
                            elif severity == "major" and svc["status"] != "major_outage":
                                svc["status"] = "partial_outage"
                            elif svc["status"] == "operational":
                                svc["status"] = "degraded"
        except Exception as exc:
            logger.warning("Failed to load active incidents for status page: %s", exc)

    # Determine overall status
    overall = "operational"
    if any(svc["status"] == "major_outage" for svc in services):
        overall = "major_outage"
    elif any(svc["status"] == "partial_outage" for svc in services):
        overall = "partial_outage"
    elif any(svc["status"] == "degraded" for svc in services):
        overall = "degraded"

    return PublicStatusResponse(
        overall_status=overall,
        active_incidents=active_incidents,
        services=services,
    )
