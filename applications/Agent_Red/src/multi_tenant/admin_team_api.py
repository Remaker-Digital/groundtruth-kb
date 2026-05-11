# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Admin Team Management API — merchant team member CRUD (WI #179).

Provides REST endpoints for the merchant admin dashboard's TeamManager
component:

    GET    /api/admin/team              — List team members with filtering & pagination
    GET    /api/admin/team/whoami       — Get caller identity and role
    GET    /api/admin/team/{member_id}  — Get single team member
    POST   /api/admin/team              — Create team member (with per-user API key)
    PUT    /api/admin/team/{member_id}  — Update team member (role, settings)
    DELETE /api/admin/team/{member_id}  — Remove team member (hard delete + audit)
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
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext, generate_user_api_key, hash_api_key
from src.multi_tenant.cosmos_schema import (
    ESCALATION_CATEGORIES,
    AuditEventType,
    ConversationStatus,
    TeamMemberRole,
)
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import (
    AuditLogRepository,
    ConversationRepository,
    DocumentNotFoundError,
    TeamMemberRepository,
)

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


class TeamMemberResponse(CamelCaseModel):
    """A single team member."""

    id: str
    tenant_id: str
    email: str
    display_name: str
    role: str
    is_active: bool = True
    escalation_categories: list[str] = Field(default_factory=list)
    staff_domain_tags: list[str] = Field(default_factory=list)
    max_concurrent_conversations: int = 5
    user_api_key_prefix: str | None = Field(
        default=None, description="First 12 chars of the API key for display (ar_user_rema...)"
    )
    user_api_key: str | None = Field(
        default=None,
        description="Full API key — returned ONCE on creation or rotation, never stored",
    )
    unresolved_escalation_count: int = 0
    created_at: str
    updated_at: str
    last_login_at: str | None = None
    invited_by: str | None = None
    # MFA fields (WI #295)
    mfa_enabled: bool = False
    mfa_opt_out: bool = False
    mfa_enrolled_at: str | None = None
    phone_number_set: bool = False
    phone_verified: bool = False


class TeamListResponse(CamelCaseModel):
    """Paginated list of team members."""

    tenant_id: str
    total_count: int = Field(description="Total matching members")
    offset: int
    limit: int
    members: list[TeamMemberResponse]


class CreateTeamMemberRequest(CamelCaseModel):
    """Request body for POST /api/team."""

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
    staff_domain_tags: list[str] = Field(
        default_factory=list,
        description="Domain tags controlling which private-scope agents this member can interact with at runtime",
    )


class UpdateTeamMemberRequest(CamelCaseModel):
    """Request body for PUT /api/team/{member_id}."""

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
    staff_domain_tags: list[str] | None = Field(
        default=None,
        description="Domain tags controlling which private-scope agents this member can interact with at runtime",
    )


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_team_repo: TeamMemberRepository | None = None
_audit_repo: AuditLogRepository | None = None
_conv_repo: ConversationRepository | None = None
_mfa_totp_service: Any = None


def configure_admin_team_services(
    team_repo: TeamMemberRepository,
    audit_repo: AuditLogRepository | None = None,
    conv_repo: ConversationRepository | None = None,
    mfa_totp_service: Any = None,
) -> None:
    """Wire the admin team API to its backing repository.

    Called during app startup after TeamMemberRepository is initialised.
    """
    global _team_repo, _audit_repo, _conv_repo, _mfa_totp_service
    _team_repo = team_repo
    _audit_repo = audit_repo
    _conv_repo = conv_repo
    _mfa_totp_service = mfa_totp_service
    logger.info("Admin team management API services configured")


def _get_repo() -> TeamMemberRepository:
    """Get the TeamMemberRepository, raising 503 if not initialised."""
    if _team_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin team management services not initialised",
        )
    return _team_repo


async def _audit(
    event_type: AuditEventType,
    tenant_id: str,
    actor: str = "admin",
    payload: dict[str, Any] | None = None,
) -> None:
    """Best-effort audit log write — never raises."""
    if _audit_repo is None:
        return
    try:
        await _audit_repo.log_event(
            event_type=event_type,
            tenant_id=tenant_id,
            actor=actor,
            actor_type="admin",
            payload=payload or {},
        )
    except Exception:
        logger.warning("Failed to write audit log: %s", event_type.value, exc_info=True)


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
        staff_domain_tags=doc.get("staff_domain_tags", []),
        max_concurrent_conversations=doc.get("max_concurrent_conversations", 5),
        user_api_key_prefix=doc.get("user_api_key_prefix"),
        unresolved_escalation_count=doc.get("unresolved_escalation_count", 0),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        last_login_at=doc.get("last_login_at"),
        invited_by=doc.get("invited_by"),
        # MFA fields (WI #295)
        mfa_enabled=doc.get("mfa_enabled", False),
        mfa_opt_out=doc.get("mfa_opt_out", False),
        mfa_enrolled_at=doc.get("mfa_enrolled_at"),
        phone_number_set=bool(doc.get("phone_number")),
        phone_verified=doc.get("phone_verified", False),
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
    description=(
        "Returns a paginated list of team members. Supports filtering by role and active status, ordered by most "
        "recently updated first."
    ),
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

    # Enrich escalation agents with unresolved escalation counts (D57)
    if _conv_repo:
        for m in members_raw:
            if m.get("role") == "escalation_agent":
                try:
                    count = await _conv_repo.count_filtered(
                        ctx.tenant_id,
                        status=ConversationStatus.ESCALATED,
                        assigned_to=m["id"],
                    )
                    m["unresolved_escalation_count"] = count
                except Exception:
                    m["unresolved_escalation_count"] = 0

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


class WhoamiResponse(CamelCaseModel):
    """Response for GET /api/admin/team/whoami."""

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
    description=(
        "Returns the authenticated caller's role and identity. Used by the admin frontend to determine nav visibility "
        "and permissions."
    ),
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
    description=(
        "Creates a new team member with a per-user API key. The member is immediately active. The raw API key is "
        "returned ONCE in the response."
    ),
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
            detail=f"Cannot create a team member with the '{request.role}' role. This role is auto-provisioned only.",
        )

    # Validate escalation_categories
    if request.escalation_categories:
        invalid_cats = [c for c in request.escalation_categories if c not in ESCALATION_CATEGORIES]
        if invalid_cats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid escalation categories: {invalid_cats}. Valid values: {ESCALATION_CATEGORIES}",
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

    now = datetime.now(UTC).isoformat()
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
        staff_domain_tags=request.staff_domain_tags,
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

    await _audit(
        AuditEventType.TEAM_MEMBER_ADDED,
        tenant_id=ctx.tenant_id,
        actor=getattr(ctx, "team_member_email", "admin"),
        payload={"email": request.email, "role": request.role, "display_name": request.display_name or ""},
    )

    # Fire-and-forget: send team invitation email to the invitee
    try:
        import asyncio

        from src.multi_tenant.alert_delivery import send_team_invite_alert

        inviter = getattr(ctx, "team_member_email", None) or "Your team administrator"
        asyncio.ensure_future(
            send_team_invite_alert(
                tenant_id=ctx.tenant_id,
                invitee_email=request.email,
                inviter_name=inviter,
                role=request.role,
            )
        )
    except Exception:
        logger.debug("Team invite alert skipped (alert service not configured)")

    response = _build_member_response(doc.model_dump(), ctx.tenant_id)
    # Attach the raw API key — returned ONCE, never stored or retrievable
    response.user_api_key = raw_api_key
    return response


# ---------------------------------------------------------------------------
# POST /api/team/{member_id}/resend-invite — Re-send team invitation
# ---------------------------------------------------------------------------


class ResendInviteResponse(CamelCaseModel):
    """Response for re-send invitation."""

    success: bool
    message: str


@router.post(
    "/{member_id}/resend-invite",
    response_model=ResendInviteResponse,
    summary="Re-send team invitation",
    description="Re-sends the invitation email to an existing team member. "
    "Only admins and superadmins may re-send invitations.",
    responses={
        404: {"description": "Team member not found"},
        503: {"description": "Team management services not initialized"},
    },
)
async def resend_team_invite(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ResendInviteResponse:
    """Re-send the invitation email to an existing team member."""
    repo = _get_repo()

    # Look up the member
    doc = await repo.read(ctx.tenant_id, member_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Team member not found")

    member_email = doc.get("email")
    member_role = doc.get("role", "agent")

    if not member_email:
        raise HTTPException(
            status_code=400,
            detail="Team member has no email address",
        )

    # Fire-and-forget: re-send invitation email
    try:
        import asyncio

        from src.multi_tenant.alert_delivery import send_team_invite_alert

        inviter = getattr(ctx, "team_member_email", None) or "Your team administrator"
        asyncio.ensure_future(
            send_team_invite_alert(
                tenant_id=ctx.tenant_id,
                invitee_email=member_email,
                inviter_name=inviter,
                role=member_role,
            )
        )
        logger.info(
            "Re-sent team invite: email=%s tenant=%s",
            member_email,
            ctx.tenant_id[:8],
        )
    except Exception as exc:
        logger.warning("Failed to re-send team invite: %s", exc)
        return ResendInviteResponse(
            success=False,
            message="Could not send invitation email. Please try again.",
        )

    return ResendInviteResponse(
        success=True,
        message=f"Invitation re-sent to {member_email}",
    )


# ---------------------------------------------------------------------------
# PUT /api/team/{member_id} — Update team member
# ---------------------------------------------------------------------------


@router.put(
    "/{member_id}",
    response_model=TeamMemberResponse,
    summary="Update team member",
    description=(
        "Updates an existing team member. Only provided fields are updated; omitted fields retain their current "
        "values. Superadmin members can only be modified by other superadmins."
    ),
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
            detail=f"Cannot assign the '{request.role}' role via update. This role is auto-provisioned only.",
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
                detail=f"Invalid escalation categories: {invalid_cats}. Valid values: {ESCALATION_CATEGORIES}",
            )
        # Determine the effective role after update
        effective_role = request.role if request.role is not None else existing_role
        if effective_role != "escalation_agent":
            raise HTTPException(
                status_code=400,
                detail="escalation_categories can only be set for the 'escalation_agent' role.",
            )

    # Build updates — split encrypted fields from safe-to-patch fields.
    # SPEC-1843: encrypted fields (display_name, email) must use
    # read-modify-write via update_encrypted_fields(), not patch().
    now = datetime.now(UTC).isoformat()
    patch_operations: list[dict[str, Any]] = [
        {"op": "set", "path": "/updated_at", "value": now},
    ]
    encrypted_updates: dict[str, Any] = {}

    if request.display_name is not None:
        encrypted_updates["display_name"] = request.display_name
    if request.role is not None:
        patch_operations.append({"op": "set", "path": "/role", "value": request.role})
        # Clear escalation_categories when changing away from escalation_agent
        if request.role != "escalation_agent" and request.escalation_categories is None:
            patch_operations.append({"op": "set", "path": "/escalation_categories", "value": []})
    if request.escalation_categories is not None:
        patch_operations.append({"op": "set", "path": "/escalation_categories", "value": request.escalation_categories})
    if request.max_concurrent_conversations is not None:
        patch_operations.append(
            {"op": "set", "path": "/max_concurrent_conversations", "value": request.max_concurrent_conversations}
        )
    if request.is_active is not None:
        patch_operations.append({"op": "set", "path": "/is_active", "value": request.is_active})
    if request.staff_domain_tags is not None:
        patch_operations.append({"op": "set", "path": "/staff_domain_tags", "value": request.staff_domain_tags})

    # Patch non-encrypted fields
    await repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=member_id,
        operations=patch_operations,
    )

    # Update encrypted fields via read-modify-write
    if encrypted_updates:
        encrypted_updates["updated_at"] = now
        await repo.update_encrypted_fields(
            tenant_id=ctx.tenant_id,
            document_id=member_id,
            field_updates=encrypted_updates,
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
    if request.staff_domain_tags is not None:
        updated["staff_domain_tags"] = request.staff_domain_tags
    updated["updated_at"] = now

    logger.info(
        "Team member updated: id=%s tenant=%s",
        member_id,
        ctx.tenant_id[:8],
    )

    # Build change summary for audit
    changes: dict[str, Any] = {}
    if request.role is not None and request.role != existing.get("role"):
        changes["role"] = {"from": existing.get("role"), "to": request.role}
    if request.display_name is not None and request.display_name != existing.get("display_name"):
        changes["display_name"] = {"from": existing.get("display_name"), "to": request.display_name}
    if request.escalation_categories is not None:
        changes["escalation_categories"] = request.escalation_categories
    if changes:
        await _audit(
            AuditEventType.TEAM_MEMBER_UPDATED,
            tenant_id=ctx.tenant_id,
            actor=getattr(ctx, "team_member_email", "admin"),
            payload={"member_id": member_id, "email": existing.get("email", ""), "changes": changes},
        )

    return _build_member_response(updated, ctx.tenant_id)


# ---------------------------------------------------------------------------
# DELETE /api/team/{member_id} — Remove team member (hard delete)
# ---------------------------------------------------------------------------


class DeleteTeamMemberResponse(CamelCaseModel):
    """Response for successful team member deletion."""

    id: str
    deleted_at: str


@router.delete(
    "/{member_id}",
    response_model=DeleteTeamMemberResponse,
    summary="Remove team member",
    description=(
        "Permanently removes the team member. An audit log entry is created. Superadmin members cannot be removed."
    ),
    responses={
        400: {"description": "Cannot remove a superadmin member"},
        404: {"description": "Team member not found"},
        503: {"description": "Team management services not initialized"},
    },
)
async def delete_team_member(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeleteTeamMemberResponse:
    """Permanently remove a team member.

    The Cosmos DB document is deleted. An audit log entry preserves
    the record of who was removed and by whom.

    Superadmin members cannot be removed.
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

    # Superadmins cannot be removed
    existing_role = existing.get("role", "")
    caller_is_superadmin = getattr(ctx, "team_member_role", None) == TeamMemberRole.SUPERADMIN
    if existing_role in PROTECTED_ROLES:
        if not caller_is_superadmin:
            raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")
        raise HTTPException(
            status_code=400,
            detail="Cannot remove a superadmin member.",
        )

    # Hard delete the document
    await repo.delete(ctx.tenant_id, member_id)

    now = datetime.now(UTC).isoformat()

    # Audit log (best-effort)
    await _audit(
        AuditEventType.TEAM_MEMBER_REMOVED,
        tenant_id=ctx.tenant_id,
        actor=getattr(ctx, "team_member_email", "admin"),
        payload={
            "member_id": member_id,
            "email": existing.get("email", ""),
            "role": existing_role,
            "display_name": existing.get("display_name", ""),
        },
    )

    logger.info(
        "Team member removed: id=%s email=%s tenant=%s",
        member_id,
        existing.get("email", ""),
        ctx.tenant_id[:8],
    )

    return DeleteTeamMemberResponse(
        id=member_id,
        deleted_at=now,
    )


# ---------------------------------------------------------------------------
# POST /api/team/{member_id}/rotate-key — Rotate user API key
# ---------------------------------------------------------------------------


class RotateKeyResponse(CamelCaseModel):
    """Response for successful key rotation."""

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
    now = datetime.now(UTC).isoformat()

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


# ---------------------------------------------------------------------------
# MFA management endpoints (WI #295 Phase 4)
# ---------------------------------------------------------------------------


class MfaStatusResponse(CamelCaseModel):
    """MFA enrollment status for a team member."""

    mfa_enabled: bool = False
    enrolled_at: str | None = None
    backup_codes_remaining: int = 0
    mfa_opt_out: bool = False
    phone_number_set: bool = False
    phone_verified: bool = False


class MfaEnrollStartResponse(CamelCaseModel):
    """MFA enrollment artifacts — returned once, cannot be retrieved again."""

    qr_code_data_url: str
    provisioning_uri: str
    backup_codes: list[str]


class MfaEnrollConfirmRequest(CamelCaseModel):
    """Confirm MFA enrollment with a TOTP code."""

    code: str = Field(description="6-digit TOTP code from authenticator app")
    backup_code_hashes: list[str] = Field(description="Hashed backup codes from enrollment")


class MfaDisableRequest(CamelCaseModel):
    """Disable MFA — requires current TOTP code for confirmation."""

    code: str = Field(description="6-digit TOTP code to confirm identity")


def _get_mfa_service():
    """Get the MfaTotpService, raising 503 if not initialised."""
    if _mfa_totp_service is None:
        raise HTTPException(
            status_code=503,
            detail="MFA services not initialised",
        )
    return _mfa_totp_service


@router.get(
    "/{member_id}/mfa/status",
    response_model=MfaStatusResponse,
    summary="Get MFA enrollment status",
)
async def get_mfa_status(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaStatusResponse:
    """Get MFA enrollment status for a team member.

    Admins can check any member's status. Non-admins can only check their own.
    """
    repo = _get_repo()

    # Non-admins can only check their own status
    caller_role = getattr(ctx, "team_member_role", None)
    caller_id = getattr(ctx, "team_member_id", None)
    if caller_role and caller_role not in (TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN):
        if caller_id != member_id:
            raise HTTPException(status_code=403, detail="Cannot view other members' MFA status")

    try:
        doc = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    return MfaStatusResponse(
        mfa_enabled=doc.get("mfa_enabled", False),
        enrolled_at=doc.get("mfa_enrolled_at"),
        backup_codes_remaining=len(doc.get("mfa_backup_code_hashes", [])),
        mfa_opt_out=doc.get("mfa_opt_out", False),
        phone_number_set=bool(doc.get("phone_number")),
        phone_verified=doc.get("phone_verified", False),
    )


@router.post(
    "/{member_id}/mfa/enroll",
    response_model=MfaEnrollStartResponse,
    summary="Start MFA enrollment",
)
async def start_mfa_enrollment(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> MfaEnrollStartResponse:
    """Start TOTP MFA enrollment for a team member.

    Returns a QR code, provisioning URI, and backup codes.
    The backup codes are shown ONCE and cannot be retrieved again.
    """
    repo = _get_repo()
    mfa = _get_mfa_service()

    # Only the member themselves or an admin can enroll
    caller_role = getattr(ctx, "team_member_role", None)
    caller_id = getattr(ctx, "team_member_id", None)
    if caller_role and caller_role not in (TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN):
        if caller_id != member_id:
            raise HTTPException(status_code=403, detail="Cannot enroll MFA for other members")

    try:
        doc = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    if doc.get("mfa_enabled"):
        raise HTTPException(status_code=400, detail="MFA is already enrolled. Disable first to re-enroll.")

    result = await mfa.start_enrollment(doc)

    return MfaEnrollStartResponse(
        qr_code_data_url=result["qr_code_data_url"],
        provisioning_uri=result["provisioning_uri"],
        backup_codes=result["backup_codes"],
    )


@router.post(
    "/{member_id}/mfa/confirm",
    summary="Confirm MFA enrollment",
)
async def confirm_mfa_enrollment(
    member_id: str,
    body: MfaEnrollConfirmRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Confirm MFA enrollment by verifying the first TOTP code.

    Must be called after start_mfa_enrollment. The provided code proves
    the authenticator app is correctly configured.
    """
    repo = _get_repo()
    mfa = _get_mfa_service()

    # Only the member themselves or an admin can confirm
    caller_role = getattr(ctx, "team_member_role", None)
    caller_id = getattr(ctx, "team_member_id", None)
    if caller_role and caller_role not in (TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN):
        if caller_id != member_id:
            raise HTTPException(status_code=403, detail="Cannot confirm MFA for other members")

    try:
        doc = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    confirmed = await mfa.confirm_enrollment(doc, body.code, body.backup_code_hashes)
    if not confirmed:
        raise HTTPException(status_code=401, detail="Invalid TOTP code. Please try again.")

    await _audit(AuditEventType.TEAM_MEMBER_UPDATED, ctx.tenant_id, actor=member_id, payload={"action": "mfa_enrolled"})

    return {"status": "enrolled", "message": "MFA enrollment confirmed successfully."}


@router.post(
    "/{member_id}/mfa/disable",
    summary="Disable MFA",
)
async def disable_mfa(
    member_id: str,
    body: MfaDisableRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Disable MFA for a team member. Requires a valid TOTP code.

    Superadmins can disable any member's MFA. Other users can only
    disable their own MFA.
    """
    repo = _get_repo()
    mfa = _get_mfa_service()

    caller_role = getattr(ctx, "team_member_role", None)
    caller_id = getattr(ctx, "team_member_id", None)
    caller_is_superadmin = caller_role == TeamMemberRole.SUPERADMIN

    # Only the member or a superadmin can disable MFA
    if not caller_is_superadmin and caller_id != member_id:
        raise HTTPException(status_code=403, detail="Cannot disable MFA for other members")

    try:
        doc = await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    if not doc.get("mfa_enabled"):
        raise HTTPException(status_code=400, detail="MFA is not enrolled.")

    disabled = await mfa.disable_mfa(doc, body.code)
    if not disabled:
        raise HTTPException(status_code=401, detail="Invalid TOTP code.")

    await _audit(AuditEventType.TEAM_MEMBER_UPDATED, ctx.tenant_id, actor=member_id, payload={"action": "mfa_disabled"})

    return {"status": "disabled", "message": "MFA has been disabled."}


@router.post(
    "/{member_id}/mfa/grant-opt-out",
    summary="Grant MFA opt-out (superadmin only)",
)
async def grant_mfa_opt_out(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Grant a team member an MFA opt-out. Superadmin only.

    When opted out, the member skips 2FA even if they have an admin role.
    This is a deliberate bypass for specific business needs.
    """
    repo = _get_repo()

    caller_role = getattr(ctx, "team_member_role", None)
    if caller_role != TeamMemberRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Only superadmin can grant MFA opt-out")

    try:
        await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    now = datetime.now(UTC).isoformat()
    await repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=member_id,
        operations=[
            {"op": "set", "path": "/mfa_opt_out", "value": True},
            {"op": "set", "path": "/updated_at", "value": now},
        ],
    )

    await _audit(
        AuditEventType.TEAM_MEMBER_UPDATED,
        ctx.tenant_id,
        actor=getattr(ctx, "team_member_id", "admin"),
        payload={"action": "mfa_opt_out_granted", "member_id": member_id},
    )

    return {"status": "opt_out_granted", "message": f"MFA opt-out granted for member {member_id}."}


@router.post(
    "/{member_id}/mfa/revoke-opt-out",
    summary="Revoke MFA opt-out (superadmin only)",
)
async def revoke_mfa_opt_out(
    member_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Revoke a team member's MFA opt-out. Superadmin only.

    The member will be required to complete 2FA on next admin login.
    """
    repo = _get_repo()

    caller_role = getattr(ctx, "team_member_role", None)
    if caller_role != TeamMemberRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Only superadmin can revoke MFA opt-out")

    try:
        await repo.read(ctx.tenant_id, member_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Team member {member_id} not found")

    now = datetime.now(UTC).isoformat()
    await repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=member_id,
        operations=[
            {"op": "set", "path": "/mfa_opt_out", "value": False},
            {"op": "set", "path": "/updated_at", "value": now},
        ],
    )

    await _audit(
        AuditEventType.TEAM_MEMBER_UPDATED,
        ctx.tenant_id,
        actor=getattr(ctx, "team_member_id", "admin"),
        payload={"action": "mfa_opt_out_revoked", "member_id": member_id},
    )

    return {"status": "opt_out_revoked", "message": f"MFA opt-out revoked for member {member_id}."}


# ---------------------------------------------------------------------------
# SPEC-0761: Customer admin account provisioning
# ---------------------------------------------------------------------------


async def provision_customer_admin(
    tenant_id: str,
    customer_email: str,
    display_name: str = "Account Administrator",
) -> dict[str, str]:
    """Create a standard admin account for customer handoff (SPEC-0761).

    Called during tenant provisioning to create a second admin account
    for the customer's email address. This account is separate from the
    hidden superadmin and is the account the customer uses day-to-day.

    The customer_email MUST differ from the superadmin email.

    Returns:
        Dict with member_id, email, and raw API key (shown once).
    """
    repo = _get_repo()

    # Guard: check duplicate
    existing = await repo.find_by_email(tenant_id, customer_email)
    if existing is not None:
        return {
            "member_id": existing.get("id", ""),
            "email": customer_email,
            "api_key": "(already exists)",
            "created": False,
        }

    now = datetime.now(UTC).isoformat()
    member_id = f"{tenant_id}:{customer_email}"

    raw_api_key = generate_user_api_key(tenant_id)
    key_hash = hash_api_key(raw_api_key)
    key_prefix = raw_api_key[:12] + "..."

    from src.multi_tenant.cosmos_schema import TeamMemberDocument

    doc = TeamMemberDocument(
        id=member_id,
        tenant_id=tenant_id,
        email=customer_email,
        display_name=display_name,
        role=TeamMemberRole.ADMIN,
        is_active=True,
        escalation_categories=[],
        max_concurrent_conversations=5,
        user_api_key_hash=key_hash,
        user_api_key_prefix=key_prefix,
        created_at=now,
        updated_at=now,
        invited_by="provisioning",
    )

    await repo.create(tenant_id, doc)

    logger.info(
        "Customer admin provisioned: tenant=%s email=%s member_id=%s",
        tenant_id,
        customer_email,
        member_id,
    )

    return {
        "member_id": member_id,
        "email": customer_email,
        "api_key": raw_api_key,
        "created": True,
    }
