"""Admin Team Management API — merchant team member CRUD (WI #179).

Provides REST endpoints for the merchant admin dashboard's TeamManager
component:

    GET    /api/admin/team              — List team members with filtering & pagination
    GET    /api/admin/team/whoami       — Get caller identity and role
    GET    /api/admin/team/{member_id}  — Get single team member
    POST   /api/admin/team              — Create team member (with per-user API key)
    PUT    /api/admin/team/{member_id}  — Update team member (role, settings)
    DELETE /api/admin/team/{member_id}  — Deactivate team member
    POST   /api/admin/team/{member_id}/rotate-key — Rotate user API key

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

from src.multi_tenant.auth import TenantContext, generate_user_api_key, hash_api_key
from src.multi_tenant.cosmos_schema import ESCALATION_CATEGORIES, TeamMemberRole
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import DocumentNotFoundError, TeamMemberRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Valid roles
# ---------------------------------------------------------------------------

VALID_ROLES = {r.value for r in TeamMemberRole}
# Roles that cannot be assigned via the API (auto-provisioned only)
PROTECTED_ROLES = {"superadmin"}


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
    escalation_categories: list[str] = Field(default_factory=list)
    max_concurrent_conversations: int = 5
    user_api_key_prefix: str | None = Field(
        default=None, description="First 12 chars of the API key for display (ar_user_rema...)"
    )
    user_api_key: str | None = Field(
        default=None,
        description="Full API key — returned ONCE on creation or rotation, never stored",
    )
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
        description="Team member email address (unique within tenant, immutable after creation)",
    )
    display_name: str = Field(
        min_length=1,
        max_length=200,
        description="Display name shown in inbox and notes",
    )
    role: str = Field(
        description="Permission role: admin, escalation_agent, or viewer",
    )
    escalation_categories: list[str] = Field(
        default_factory=list,
        description="Escalation categories for escalation_agent role: "
        "service, support, sales, account, technical_assistance, general_inquiry",
    )
    max_concurrent_conversations: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Max simultaneous escalated conversations (escalation_agent role)",
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
        description="Permission role: admin, escalation_agent, or viewer",
    )
    escalation_categories: list[str] | None = Field(
        default=None,
        description="Escalation categories (escalation_agent role only)",
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


def _build_member_response(doc: dict[str, Any], tenant_id: str) -> TeamMemberResponse:
    """Build a TeamMemberResponse from a Cosmos DB document.

    Centralises field extraction so all endpoints return consistent data.
    """
    return TeamMemberResponse(
        id=doc.get("id", ""),
        tenant_id=tenant_id,
        email=doc.get("email", ""),
        display_name=doc.get("display_name", ""),
        role=doc.get("role", "viewer"),
        is_active=doc.get("is_active", True),
        escalation_categories=doc.get("escalation_categories", []),
        max_concurrent_conversations=doc.get("max_concurrent_conversations", 5),
        user_api_key_prefix=doc.get("user_api_key_prefix"),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        last_login_at=doc.get("last_login_at"),
        invited_by=doc.get("invited_by"),
    )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/team", tags=["admin-team"])


# ---------------------------------------------------------------------------
# GET /api/team — List team members with filtering & pagination
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=TeamListResponse,
    summary="List team members",
    description="Returns a paginated list of team members. Supports filtering by role and active status, ordered by most recently updated first.",
    responses={
        400: {"description": "Invalid role filter value"},
        503: {"description": "Team management services not initialized"},
    },
)
async def list_team_members(
    role: str | None = Query(
        None,
        description="Filter by role (superadmin, admin, escalation_agent, viewer)",
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

    Superadmin members are only visible to other superadmins.
    """
    repo = _get_repo()

    # Validate role if provided
    if role is not None and role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{role}'. Valid values: {sorted(VALID_ROLES)}",
        )

    # Non-superadmins cannot filter by or see superadmin members
    caller_is_superadmin = getattr(ctx, "team_member_role", None) == TeamMemberRole.SUPERADMIN
    if role == "superadmin" and not caller_is_superadmin:
        raise HTTPException(
            status_code=400,
            detail="Invalid role filter 'superadmin'.",
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

    # Filter out superadmin members for non-superadmin callers
    if not caller_is_superadmin:
        members_raw = [m for m in members_raw if m.get("role") != "superadmin"]
        # Adjust count (superadmins excluded from visible list)
        total_count = len(members_raw) if offset == 0 else total_count

    members = [_build_member_response(m, ctx.tenant_id) for m in members_raw]

    return TeamListResponse(
        tenant_id=ctx.tenant_id,
        total_count=total_count,
        offset=offset,
        limit=limit,
        members=members,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/team/whoami — Caller identity (must be before /{member_id})
# ---------------------------------------------------------------------------


class WhoamiResponse(BaseModel):
    """Response for GET /api/admin/team/whoami."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    tenant_id: str
    role: str | None = None
    team_member_id: str | None = None
    email: str | None = None
    auth_method: str = Field(
        default="tenant_api_key",
        description="How the caller authenticated: 'user_api_key' or 'tenant_api_key'.",
    )


@router.get(
    "/whoami",
    response_model=WhoamiResponse,
    status_code=200,
    summary="Get caller identity",
    description="Returns the authenticated caller's role and identity. Used by the admin frontend to determine nav visibility and permissions.",
)
async def whoami(
    ctx: TenantContext = Depends(get_tenant_context),
) -> WhoamiResponse:
    """Return the caller's identity based on their API key.

    For per-user API keys: returns role, member ID, and email.
    For legacy tenant API keys: returns role=admin (implicit).
    """
    if ctx.team_member_role is not None:
        return WhoamiResponse(
            tenant_id=ctx.tenant_id,
            role=ctx.team_member_role.value,
            team_member_id=ctx.team_member_id,
            email=ctx.team_member_email,
            auth_method="user_api_key",
        )

    # Legacy tenant API key — treated as admin
    return WhoamiResponse(
        tenant_id=ctx.tenant_id,
        role="admin",
        auth_method="tenant_api_key",
    )


# ---------------------------------------------------------------------------
# GET /api/team/{member_id} — Get single team member
# ---------------------------------------------------------------------------


@router.get(
    "/{member_id}",
    response_model=TeamMemberResponse,
    summary="Get team member",
    description="Returns a single team member by ID.",
    responses={
        404: {"description": "Team member not found"},
        503: {"description": "Team management services not initialized"},
    },
)
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

    # Superadmin records hidden from non-superadmins
    caller_is_superadmin = getattr(ctx, "team_member_role", None) == TeamMemberRole.SUPERADMIN
    if doc.get("role") == "superadmin" and not caller_is_superadmin:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    return _build_member_response(doc, ctx.tenant_id)


# ---------------------------------------------------------------------------
# POST /api/team — Create / invite team member
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=TeamMemberResponse,
    status_code=201,
    summary="Create team member",
    description="Creates a new team member with a per-user API key. The member is immediately active. The raw API key is returned ONCE in the response.",
    responses={
        400: {"description": "Invalid role, protected role, or invalid escalation categories"},
        409: {"description": "Team member with this email already exists"},
        503: {"description": "Team management services not initialized"},
    },
)
async def create_team_member(
    request: CreateTeamMemberRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TeamMemberResponse:
    """Create a new team member with a per-user API key.

    The member is immediately active and can access the admin dashboard
    based on their assigned role. A unique API key (ar_user_...) is
    generated and returned ONCE in the response — it cannot be retrieved
    again, only rotated.
    """
    repo = _get_repo()

    # Validate role
    if request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{request.role}'. Valid values: {sorted(VALID_ROLES)}",
        )

    # Protected roles cannot be created via API
    if request.role in PROTECTED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create a team member with the '{request.role}' role. "
            "This role is auto-provisioned only.",
        )

    # Validate escalation_categories
    if request.escalation_categories:
        invalid_cats = [c for c in request.escalation_categories if c not in ESCALATION_CATEGORIES]
        if invalid_cats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid escalation categories: {invalid_cats}. "
                f"Valid values: {ESCALATION_CATEGORIES}",
            )
        # Only escalation_agent role may have categories
        if request.role != "escalation_agent":
            raise HTTPException(
                status_code=400,
                detail="escalation_categories can only be set for the 'escalation_agent' role.",
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

    # Generate per-user API key
    raw_api_key = generate_user_api_key(ctx.tenant_id)
    key_hash = hash_api_key(raw_api_key)
    key_prefix = raw_api_key[:12] + "..."

    from src.multi_tenant.cosmos_schema import TeamMemberDocument

    doc = TeamMemberDocument(
        id=member_id,
        tenant_id=ctx.tenant_id,
        email=request.email,
        display_name=request.display_name,
        role=request.role,
        is_active=True,
        escalation_categories=request.escalation_categories,
        max_concurrent_conversations=request.max_concurrent_conversations,
        user_api_key_hash=key_hash,
        user_api_key_prefix=key_prefix,
        created_at=now,
        updated_at=now,
        invited_by=ctx.user_id,
    )

    await repo.create(ctx.tenant_id, doc)

    logger.info(
        "Team member created: email=%s role=%s tenant=%s key_prefix=%s",
        request.email,
        request.role,
        ctx.tenant_id[:8],
        key_prefix,
    )

    response = _build_member_response(doc.model_dump(), ctx.tenant_id)
    # Attach the raw API key — returned ONCE, never stored or retrievable
    response.user_api_key = raw_api_key
    return response


# ---------------------------------------------------------------------------
# PUT /api/team/{member_id} — Update team member
# ---------------------------------------------------------------------------


@router.put(
    "/{member_id}",
    response_model=TeamMemberResponse,
    summary="Update team member",
    description="Updates an existing team member. Only provided fields are updated; omitted fields retain their current values. Superadmin members can only be modified by other superadmins.",
    responses={
        400: {"description": "Invalid role, protected role assignment, or invalid escalation categories"},
        404: {"description": "Team member not found"},
        503: {"description": "Team management services not initialized"},
    },
)
async def update_team_member(
    member_id: str,
    request: UpdateTeamMemberRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TeamMemberResponse:
    """Update an existing team member.

    Only provided fields are updated. Omitted fields retain their
    current values. Protected roles (superadmin) cannot be modified
    except by another superadmin.
    """
    repo = _get_repo()

    # Validate role if provided
    if request.role is not None and request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{request.role}'. Valid values: {sorted(VALID_ROLES)}",
        )

    # Cannot promote anyone to a protected role via API
    if request.role is not None and request.role in PROTECTED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot assign the '{request.role}' role via update. "
            "This role is auto-provisioned only.",
        )

    # Read existing document to verify it exists
    try:
        existing = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Team member {member_id} not found",
        )

    # Superadmin members can only be modified by superadmins
    existing_role = existing.get("role", "")
    caller_is_superadmin = getattr(ctx, "team_member_role", None) == TeamMemberRole.SUPERADMIN
    if existing_role in PROTECTED_ROLES and not caller_is_superadmin:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    # Validate escalation_categories if provided
    if request.escalation_categories is not None:
        invalid_cats = [c for c in request.escalation_categories if c not in ESCALATION_CATEGORIES]
        if invalid_cats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid escalation categories: {invalid_cats}. "
                f"Valid values: {ESCALATION_CATEGORIES}",
            )
        # Determine the effective role after update
        effective_role = request.role if request.role is not None else existing_role
        if effective_role != "escalation_agent":
            raise HTTPException(
                status_code=400,
                detail="escalation_categories can only be set for the 'escalation_agent' role.",
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
        # Clear escalation_categories when changing away from escalation_agent
        if request.role != "escalation_agent" and request.escalation_categories is None:
            operations.append({"op": "set", "path": "/escalation_categories", "value": []})
    if request.escalation_categories is not None:
        operations.append({"op": "set", "path": "/escalation_categories", "value": request.escalation_categories})
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
        if request.role != "escalation_agent" and request.escalation_categories is None:
            updated["escalation_categories"] = []
    if request.escalation_categories is not None:
        updated["escalation_categories"] = request.escalation_categories
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

    return _build_member_response(updated, ctx.tenant_id)


# ---------------------------------------------------------------------------
# DELETE /api/team/{member_id} — Deactivate team member
# ---------------------------------------------------------------------------


@router.delete(
    "/{member_id}",
    response_model=DeactivateTeamMemberResponse,
    summary="Deactivate team member",
    description="Sets is_active to false so the member can no longer access the admin dashboard. The record is preserved for audit purposes. Superadmin members cannot be deactivated.",
    responses={
        400: {"description": "Cannot deactivate a superadmin member"},
        404: {"description": "Team member not found"},
        503: {"description": "Team management services not initialized"},
    },
)
async def deactivate_team_member(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeactivateTeamMemberResponse:
    """Deactivate a team member.

    Sets is_active = false so the member can no longer access the admin
    dashboard or handle escalated conversations. The record is preserved
    for audit purposes and can be reactivated via PUT with is_active=true.

    Superadmin members cannot be deactivated (except by other superadmins).
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

    # Superadmins cannot be deactivated except by other superadmins
    existing_role = existing.get("role", "")
    caller_is_superadmin = getattr(ctx, "team_member_role", None) == TeamMemberRole.SUPERADMIN
    if existing_role in PROTECTED_ROLES:
        if not caller_is_superadmin:
            # Hide the existence of superadmin from non-superadmins
            raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate a superadmin member.",
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


# ---------------------------------------------------------------------------
# POST /api/team/{member_id}/rotate-key — Rotate user API key
# ---------------------------------------------------------------------------


class RotateKeyResponse(BaseModel):
    """Response for successful key rotation."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    user_api_key: str = Field(description="New API key — returned ONCE")
    user_api_key_prefix: str = Field(description="Prefix for display")
    rotated_at: str


@router.post(
    "/{member_id}/rotate-key",
    response_model=RotateKeyResponse,
    summary="Rotate user API key",
    description="Generates a new API key for the team member, invalidating the previous key. "
    "The new key is returned ONCE and cannot be retrieved again.",
    responses={
        404: {"description": "Team member not found"},
        400: {"description": "Cannot rotate superadmin key via API"},
        503: {"description": "Team management services not initialized"},
    },
)
async def rotate_user_api_key(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> RotateKeyResponse:
    """Rotate a team member's API key.

    Generates a new key and invalidates the old one. The new key is
    returned ONCE in the response. Only admins and superadmins can
    rotate other members' keys. Members can rotate their own key
    (identified by team_member_id on ctx).
    """
    repo = _get_repo()

    try:
        existing = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Team member {member_id} not found",
        )

    # Superadmin key rotation only by superadmin
    existing_role = existing.get("role", "")
    caller_is_superadmin = getattr(ctx, "team_member_role", None) == TeamMemberRole.SUPERADMIN
    if existing_role in PROTECTED_ROLES and not caller_is_superadmin:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    # Generate new key
    raw_api_key = generate_user_api_key(ctx.tenant_id)
    key_hash = hash_api_key(raw_api_key)
    key_prefix = raw_api_key[:12] + "..."
    now = datetime.now(timezone.utc).isoformat()

    await repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=member_id,
        operations=[
            {"op": "set", "path": "/user_api_key_hash", "value": key_hash},
            {"op": "set", "path": "/user_api_key_prefix", "value": key_prefix},
            {"op": "set", "path": "/updated_at", "value": now},
        ],
    )

    logger.info(
        "API key rotated: member=%s tenant=%s new_prefix=%s",
        member_id,
        ctx.tenant_id[:8],
        key_prefix,
    )

    return RotateKeyResponse(
        id=member_id,
        user_api_key=raw_api_key,
        user_api_key_prefix=key_prefix,
        rotated_at=now,
    )
