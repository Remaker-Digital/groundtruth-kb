"""Admin Team Management API — merchant team member CRUD (WI #179).

Provides REST endpoints for the merchant admin dashboard's TeamManager
component:

    GET    /api/team              — List team members with filtering & pagination
    GET    /api/team/{member_id}  — Get single team member
    POST   /api/team              — Invite / create team member
    PUT    /api/team/{member_id}  — Update team member (role, settings)
    DELETE /api/team/{member_id}  — Deactivate team member

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* only).

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §7: WI #179 — Team Member CRUD
    - Decision #1: TenantScopedRepository enforces tenant isolation
    - TeamMemberDocument schema in cosmos_schema.py

Dependencies:
    - repository.py: TeamMemberRepository (list_members, count_members,
      find_by_email, create, read, patch, deactivate)
    - cosmos_schema.py: TeamMemberDocument, TeamMemberRole
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import DocumentNotFoundError, TeamMemberRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Valid roles
# ---------------------------------------------------------------------------

VALID_ROLES = {"owner", "admin", "agent", "viewer"}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class TeamMemberResponse(BaseModel):
    """A single team member."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    tenant_id: str
    email: str
    display_name: str
    role: str
    is_active: bool = True
    max_concurrent_conversations: int = 5
    created_at: str
    updated_at: str
    last_login_at: str | None = None
    invited_by: str | None = None


class TeamListResponse(BaseModel):
    """Paginated list of team members."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    tenant_id: str
    total_count: int = Field(description="Total matching members")
    offset: int
    limit: int
    members: list[TeamMemberResponse]


class CreateTeamMemberRequest(BaseModel):
    """Request body for POST /api/team."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    email: str = Field(
        min_length=3,
        max_length=320,
        description="Team member email address (unique within tenant)",
    )
    display_name: str = Field(
        min_length=1,
        max_length=200,
        description="Display name shown in inbox and notes",
    )
    role: str = Field(
        description="Permission role: owner, admin, agent, or viewer",
    )
    max_concurrent_conversations: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Max simultaneous escalated conversations (agent role)",
    )


class UpdateTeamMemberRequest(BaseModel):
    """Request body for PUT /api/team/{member_id}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Display name",
    )
    role: str | None = Field(
        default=None,
        description="Permission role: admin, agent, or viewer",
    )
    max_concurrent_conversations: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description="Max simultaneous escalated conversations",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether member has access",
    )


class DeactivateTeamMemberResponse(BaseModel):
    """Response for successful deactivation."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    deactivated_at: str


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_team_repo: TeamMemberRepository | None = None


def configure_admin_team_services(
    team_repo: TeamMemberRepository,
) -> None:
    """Wire the admin team API to its backing repository.

    Called during app startup after TeamMemberRepository is initialised.
    """
    global _team_repo
    _team_repo = team_repo
    logger.info("Admin team management API services configured")


def _get_repo() -> TeamMemberRepository:
    """Get the TeamMemberRepository, raising 503 if not initialised."""
    if _team_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin team management services not initialised",
        )
    return _team_repo


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/team", tags=["admin-team"])


# ---------------------------------------------------------------------------
# GET /api/team — List team members with filtering & pagination
# ---------------------------------------------------------------------------


@router.get("", response_model=TeamListResponse)
async def list_team_members(
    role: str | None = Query(
        None,
        description="Filter by role (owner, admin, agent, viewer)",
    ),
    is_active: bool | None = Query(
        None,
        description="Filter by active status (true/false, omit for all)",
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> TeamListResponse:
    """List team members for the merchant admin.

    Supports filtering by role and active status.
    Results are ordered by most recently updated first.
    """
    repo = _get_repo()

    # Validate role if provided
    if role is not None and role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{role}'. Valid values: {sorted(VALID_ROLES)}",
        )

    total_count = await repo.count_members(
        tenant_id=ctx.tenant_id,
        role=role,
        is_active=is_active,
    )

    members_raw = await repo.list_members(
        tenant_id=ctx.tenant_id,
        role=role,
        is_active=is_active,
        offset=offset,
        limit=limit,
    )

    members = [
        TeamMemberResponse(
            id=m.get("id", ""),
            tenant_id=ctx.tenant_id,
            email=m.get("email", ""),
            display_name=m.get("display_name", ""),
            role=m.get("role", "viewer"),
            is_active=m.get("is_active", True),
            max_concurrent_conversations=m.get("max_concurrent_conversations", 5),
            created_at=m.get("created_at", ""),
            updated_at=m.get("updated_at", ""),
            last_login_at=m.get("last_login_at"),
            invited_by=m.get("invited_by"),
        )
        for m in members_raw
    ]

    return TeamListResponse(
        tenant_id=ctx.tenant_id,
        total_count=total_count,
        offset=offset,
        limit=limit,
        members=members,
    )


# ---------------------------------------------------------------------------
# GET /api/team/{member_id} — Get single team member
# ---------------------------------------------------------------------------


@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TeamMemberResponse:
    """Get a single team member by ID."""
    repo = _get_repo()

    try:
        doc = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Team member {member_id} not found",
        )

    return TeamMemberResponse(
        id=doc.get("id", ""),
        tenant_id=ctx.tenant_id,
        email=doc.get("email", ""),
        display_name=doc.get("display_name", ""),
        role=doc.get("role", "viewer"),
        is_active=doc.get("is_active", True),
        max_concurrent_conversations=doc.get("max_concurrent_conversations", 5),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        last_login_at=doc.get("last_login_at"),
        invited_by=doc.get("invited_by"),
    )


# ---------------------------------------------------------------------------
# POST /api/team — Create / invite team member
# ---------------------------------------------------------------------------


@router.post("", response_model=TeamMemberResponse, status_code=201)
async def create_team_member(
    request: CreateTeamMemberRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TeamMemberResponse:
    """Create a new team member.

    The member is immediately active and can access the admin dashboard
    based on their assigned role.
    """
    repo = _get_repo()

    # Validate role
    if request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{request.role}'. Valid values: {sorted(VALID_ROLES)}",
        )

    # Cannot create a second owner
    if request.role == "owner":
        raise HTTPException(
            status_code=400,
            detail="Cannot create a team member with the 'owner' role. "
            "Each tenant has exactly one owner set during provisioning.",
        )

    # Check for duplicate email within tenant
    existing = await repo.find_by_email(ctx.tenant_id, request.email)
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=f"A team member with email '{request.email}' already exists",
        )

    now = datetime.now(timezone.utc).isoformat()
    # Document ID = tenant_id:email for deterministic lookup
    member_id = f"{ctx.tenant_id}:{request.email}"

    from src.multi_tenant.cosmos_schema import TeamMemberDocument

    doc = TeamMemberDocument(
        id=member_id,
        tenant_id=ctx.tenant_id,
        email=request.email,
        display_name=request.display_name,
        role=request.role,
        is_active=True,
        max_concurrent_conversations=request.max_concurrent_conversations,
        created_at=now,
        updated_at=now,
        invited_by=ctx.user_id,
    )

    await repo.create(ctx.tenant_id, doc)

    logger.info(
        "Team member created: email=%s role=%s tenant=%s",
        request.email,
        request.role,
        ctx.tenant_id[:8],
    )

    return TeamMemberResponse(
        id=member_id,
        tenant_id=ctx.tenant_id,
        email=request.email,
        display_name=request.display_name,
        role=request.role,
        is_active=True,
        max_concurrent_conversations=request.max_concurrent_conversations,
        created_at=now,
        updated_at=now,
        invited_by=ctx.user_id,
    )


# ---------------------------------------------------------------------------
# PUT /api/team/{member_id} — Update team member
# ---------------------------------------------------------------------------


@router.put("/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: str,
    request: UpdateTeamMemberRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TeamMemberResponse:
    """Update an existing team member.

    Only provided fields are updated. Omitted fields retain their
    current values. The owner role cannot be changed.
    """
    repo = _get_repo()

    # Validate role if provided
    if request.role is not None and request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{request.role}'. Valid values: {sorted(VALID_ROLES)}",
        )

    # Read existing document to verify it exists
    try:
        existing = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Team member {member_id} not found",
        )

    # Cannot change owner role
    if existing.get("role") == "owner" and request.role is not None and request.role != "owner":
        raise HTTPException(
            status_code=400,
            detail="Cannot change the owner's role. Transfer ownership first.",
        )

    # Cannot promote to owner
    if request.role == "owner":
        raise HTTPException(
            status_code=400,
            detail="Cannot promote a team member to 'owner' via update.",
        )

    # Build patch operations from provided fields
    now = datetime.now(timezone.utc).isoformat()
    operations: list[dict[str, Any]] = [
        {"op": "set", "path": "/updated_at", "value": now},
    ]

    if request.display_name is not None:
        operations.append({"op": "set", "path": "/display_name", "value": request.display_name})
    if request.role is not None:
        operations.append({"op": "set", "path": "/role", "value": request.role})
    if request.max_concurrent_conversations is not None:
        operations.append({"op": "set", "path": "/max_concurrent_conversations", "value": request.max_concurrent_conversations})
    if request.is_active is not None:
        operations.append({"op": "set", "path": "/is_active", "value": request.is_active})

    await repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=member_id,
        operations=operations,
    )

    # Build response from existing + updates
    updated = {**existing}
    if request.display_name is not None:
        updated["display_name"] = request.display_name
    if request.role is not None:
        updated["role"] = request.role
    if request.max_concurrent_conversations is not None:
        updated["max_concurrent_conversations"] = request.max_concurrent_conversations
    if request.is_active is not None:
        updated["is_active"] = request.is_active
    updated["updated_at"] = now

    logger.info(
        "Team member updated: id=%s tenant=%s",
        member_id,
        ctx.tenant_id[:8],
    )

    return TeamMemberResponse(
        id=member_id,
        tenant_id=ctx.tenant_id,
        email=updated.get("email", ""),
        display_name=updated.get("display_name", ""),
        role=updated.get("role", "viewer"),
        is_active=updated.get("is_active", True),
        max_concurrent_conversations=updated.get("max_concurrent_conversations", 5),
        created_at=updated.get("created_at", ""),
        updated_at=now,
        last_login_at=updated.get("last_login_at"),
        invited_by=updated.get("invited_by"),
    )


# ---------------------------------------------------------------------------
# DELETE /api/team/{member_id} — Deactivate team member
# ---------------------------------------------------------------------------


@router.delete("/{member_id}", response_model=DeactivateTeamMemberResponse)
async def deactivate_team_member(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeactivateTeamMemberResponse:
    """Deactivate a team member.

    Sets is_active = false so the member can no longer access the admin
    dashboard or handle escalated conversations. The record is preserved
    for audit purposes and can be reactivated via PUT with is_active=true.

    The tenant owner cannot be deactivated.
    """
    repo = _get_repo()

    # Verify member exists and check role
    try:
        existing = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Team member {member_id} not found",
        )

    # Cannot deactivate the owner
    if existing.get("role") == "owner":
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate the tenant owner.",
        )

    await repo.deactivate(ctx.tenant_id, member_id)

    now = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Team member deactivated: id=%s tenant=%s",
        member_id,
        ctx.tenant_id[:8],
    )

    return DeactivateTeamMemberResponse(
        id=member_id,
        deactivated_at=now,
    )
