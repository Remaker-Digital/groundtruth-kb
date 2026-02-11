"""Admin Quick Action API — contextual prompt button management (WI #226-229).

Provides REST endpoints for the merchant admin dashboard's Quick Action
Prompt Library and Page Assignment panels:

    Quick Action Prompts (library):
        GET    /api/admin/quick-actions              — List all prompts
        POST   /api/admin/quick-actions              — Create a prompt
        GET    /api/admin/quick-actions/{id}         — Get single prompt
        PUT    /api/admin/quick-actions/{id}         — Update a prompt
        DELETE /api/admin/quick-actions/{id}         — Delete a prompt

    Page Assignments (which buttons appear on which pages):
        GET    /api/admin/quick-actions/assignments          — List assignments
        PUT    /api/admin/quick-actions/assignments          — Upsert assignment
        DELETE /api/admin/quick-actions/assignments/{type}   — Delete assignment

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* and /api/config only).

Quick actions are stored inside the PreferencesDocument as arrays
(quick_actions and quick_action_assignments), not in a separate collection.
This keeps them versioned with the rest of tenant configuration.

Architecture references:
    - WI #226: Quick Action Prompt Library
    - WI #227: Page Quick Action Assignments
    - WI #228: Widget Quick Action Buttons
    - WI #229: Prompt Template Variables
    - cosmos_schema.py: QuickActionPrompt, QuickActionPageAssignment
    - repository.py: PreferencesRepository quick action methods

Dependencies:
    - repository.py: PreferencesRepository
    - cosmos_schema.py: QuickActionPrompt, QuickActionPageAssignment,
      VALID_PAGE_TYPES, TIER_DEFAULTS
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    VALID_PAGE_TYPES,
    QuickActionPageAssignment,
    QuickActionPrompt,
)
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import DocumentNotFoundError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_LABEL_LENGTH = 100
MAX_PROMPT_TEMPLATE_LENGTH = 2000
MAX_ICON_LENGTH = 50


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class QuickActionResponse(BaseModel):
    """A single quick action prompt button."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    label: str
    prompt_template: str
    icon: str | None = None
    is_active: bool = True
    sort_order: int = 0
    created_at: str
    updated_at: str


class QuickActionListResponse(BaseModel):
    """List of quick action prompts for a tenant."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    tenant_id: str
    total_count: int
    actions: list[QuickActionResponse]


class CreateQuickActionRequest(BaseModel):
    """Request body for POST /api/admin/quick-actions."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    label: str = Field(
        min_length=1,
        max_length=MAX_LABEL_LENGTH,
        description="Button text shown to customer",
    )
    prompt_template: str = Field(
        min_length=1,
        max_length=MAX_PROMPT_TEMPLATE_LENGTH,
        description="Hidden prompt sent to AI with {{variable}} placeholders",
    )
    icon: str | None = Field(
        default=None,
        max_length=MAX_ICON_LENGTH,
        description="Optional emoji or icon identifier",
    )
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, ge=0, le=999)


class UpdateQuickActionRequest(BaseModel):
    """Request body for PUT /api/admin/quick-actions/{id}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_LABEL_LENGTH,
    )
    prompt_template: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_PROMPT_TEMPLATE_LENGTH,
    )
    icon: str | None = Field(default=None, max_length=MAX_ICON_LENGTH)
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0, le=999)


class PageAssignmentResponse(BaseModel):
    """A page-to-quick-action slot assignment."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_type: str
    page_handle: str | None = None
    slot_1_action_id: str | None = None
    slot_2_action_id: str | None = None
    slot_1_action: QuickActionResponse | None = None
    slot_2_action: QuickActionResponse | None = None


class PageAssignmentListResponse(BaseModel):
    """List of page assignments for a tenant."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    tenant_id: str
    total_count: int
    assignments: list[PageAssignmentResponse]


class UpsertPageAssignmentRequest(BaseModel):
    """Request body for PUT /api/admin/quick-actions/assignments."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_type: str = Field(
        description="Page type: home, product, collection, cart, search, blog, page, all, other",
    )
    page_handle: str | None = Field(
        default=None,
        max_length=500,
        description="Specific page handle (e.g. product slug), null = all of type",
    )
    slot_1_action_id: str | None = Field(
        default=None,
        description="Quick action ID for slot 1",
    )
    slot_2_action_id: str | None = Field(
        default=None,
        description="Quick action ID for slot 2",
    )


# ---------------------------------------------------------------------------
# Service accessor (wired at startup in main.py)
# ---------------------------------------------------------------------------

_prefs_repo: Any | None = None


def configure_admin_quick_action_services(
    prefs_repo: Any,
) -> None:
    """Wire the quick action API to its backing repository.

    Called during app startup after PreferencesRepository is initialised.
    """
    global _prefs_repo
    _prefs_repo = prefs_repo
    logger.info("Admin quick action API services configured")


def _get_repo() -> Any:
    if _prefs_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Quick action services not initialised",
        )
    return _prefs_repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_tier_limit(tier: str | None, key: str) -> int:
    """Get a tier-specific limit from TIER_DEFAULTS."""
    if tier and tier in TIER_DEFAULTS:
        return TIER_DEFAULTS[tier].get(key, 5)
    return 5  # Fallback default


def _action_dict_to_response(action: dict[str, Any]) -> QuickActionResponse:
    """Convert a raw action dict to a response model."""
    return QuickActionResponse(
        id=action.get("id", ""),
        label=action.get("label", ""),
        prompt_template=action.get("prompt_template", ""),
        icon=action.get("icon"),
        is_active=action.get("is_active", True),
        sort_order=action.get("sort_order", 0),
        created_at=action.get("created_at", ""),
        updated_at=action.get("updated_at", ""),
    )


def _find_action_by_id(
    actions: list[dict[str, Any]], action_id: str,
) -> dict[str, Any] | None:
    """Find a quick action by ID in the actions list."""
    for action in actions:
        if action.get("id") == action_id:
            return action
    return None


def _enrich_assignment(
    assignment: dict[str, Any],
    actions: list[dict[str, Any]],
) -> PageAssignmentResponse:
    """Build a PageAssignmentResponse with resolved action details."""
    slot_1 = None
    slot_2 = None
    slot_1_id = assignment.get("slot_1_action_id")
    slot_2_id = assignment.get("slot_2_action_id")

    if slot_1_id:
        action = _find_action_by_id(actions, slot_1_id)
        if action:
            slot_1 = _action_dict_to_response(action)

    if slot_2_id:
        action = _find_action_by_id(actions, slot_2_id)
        if action:
            slot_2 = _action_dict_to_response(action)

    return PageAssignmentResponse(
        page_type=assignment.get("page_type", ""),
        page_handle=assignment.get("page_handle"),
        slot_1_action_id=slot_1_id,
        slot_2_action_id=slot_2_id,
        slot_1_action=slot_1,
        slot_2_action=slot_2,
    )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/quick-actions", tags=["admin-quick-actions"])


# ---------------------------------------------------------------------------
# GET /api/admin/quick-actions — List all quick action prompts
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=QuickActionListResponse,
    summary="List quick action prompts",
    description="Returns all quick action prompt buttons configured for this tenant.",
    responses={
        503: {"description": "Quick action services not initialized"},
    },
)
async def list_quick_actions(
    ctx: TenantContext = Depends(get_tenant_context),
) -> QuickActionListResponse:
    """List all quick action prompts for the authenticated tenant."""
    repo = _get_repo()
    actions = await repo.get_quick_actions(ctx.tenant_id)

    # Sort by sort_order, then created_at
    actions.sort(key=lambda a: (a.get("sort_order", 0), a.get("created_at", "")))

    return QuickActionListResponse(
        tenant_id=ctx.tenant_id,
        total_count=len(actions),
        actions=[_action_dict_to_response(a) for a in actions],
    )


# ---------------------------------------------------------------------------
# POST /api/admin/quick-actions — Create a quick action prompt
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=QuickActionResponse,
    status_code=201,
    summary="Create a quick action prompt",
    description="Creates a new quick action prompt button. Subject to tier-based limits.",
    responses={
        403: {"description": "Quick action limit reached for this tier"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def create_quick_action(
    body: CreateQuickActionRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> QuickActionResponse:
    """Create a new quick action prompt."""
    repo = _get_repo()

    # Check tier limit
    existing = await repo.get_quick_actions(ctx.tenant_id)
    max_actions = _get_tier_limit(ctx.tier, "max_quick_actions")
    if len(existing) >= max_actions:
        raise HTTPException(
            status_code=403,
            detail=f"Quick action limit reached ({max_actions} for {ctx.tier} tier). "
            f"Upgrade your plan to create more.",
        )

    now = datetime.now(timezone.utc).isoformat()
    action = QuickActionPrompt(
        id=str(uuid.uuid4()),
        label=body.label,
        prompt_template=body.prompt_template,
        icon=body.icon,
        is_active=body.is_active,
        sort_order=body.sort_order,
        created_at=now,
        updated_at=now,
    )

    action_dict = action.model_dump()
    await repo.upsert_quick_action(ctx.tenant_id, action_dict)

    logger.info(
        "Quick action created: tenant=%s id=%s label=%s",
        ctx.tenant_id[:8], action.id[:8], action.label[:30],
    )
    return _action_dict_to_response(action_dict)


# ---------------------------------------------------------------------------
# GET /api/admin/quick-actions/assignments — List page assignments
# (MUST be before /{action_id} to avoid shadowing)
# ---------------------------------------------------------------------------


@router.get(
    "/assignments",
    response_model=PageAssignmentListResponse,
    summary="List page assignments",
    description="Returns all page-to-quick-action assignments for this tenant, "
    "with resolved action details for each slot.",
    responses={
        503: {"description": "Quick action services not initialized"},
    },
)
async def list_page_assignments(
    ctx: TenantContext = Depends(get_tenant_context),
) -> PageAssignmentListResponse:
    """List all page assignments with resolved action details."""
    repo = _get_repo()
    assignments = await repo.get_page_assignments(ctx.tenant_id)
    actions = await repo.get_quick_actions(ctx.tenant_id)

    return PageAssignmentListResponse(
        tenant_id=ctx.tenant_id,
        total_count=len(assignments),
        assignments=[_enrich_assignment(a, actions) for a in assignments],
    )


# ---------------------------------------------------------------------------
# PUT /api/admin/quick-actions/assignments — Upsert page assignment
# ---------------------------------------------------------------------------


@router.put(
    "/assignments",
    response_model=PageAssignmentResponse,
    summary="Create or update a page assignment",
    description="Assigns quick action buttons to a page type (and optionally a specific "
    "page handle). Each page can have up to 2 action slots.",
    responses={
        400: {"description": "Invalid page_type"},
        403: {"description": "Assignment limit reached for this tier"},
        404: {"description": "Referenced action ID not found"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def upsert_page_assignment(
    body: UpsertPageAssignmentRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> PageAssignmentResponse:
    """Create or update a page-to-quick-action assignment."""
    repo = _get_repo()

    # Validate page_type
    if body.page_type not in VALID_PAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid page_type '{body.page_type}'. "
            f"Valid values: {sorted(VALID_PAGE_TYPES)}",
        )

    # Validate that referenced action IDs exist
    actions = await repo.get_quick_actions(ctx.tenant_id)
    action_ids = {a.get("id") for a in actions}

    if body.slot_1_action_id and body.slot_1_action_id not in action_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Quick action '{body.slot_1_action_id}' not found",
        )
    if body.slot_2_action_id and body.slot_2_action_id not in action_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Quick action '{body.slot_2_action_id}' not found",
        )

    # Check tier limit for new assignments
    existing_assignments = await repo.get_page_assignments(ctx.tenant_id)
    is_new = not any(
        a.get("page_type") == body.page_type
        and a.get("page_handle") == body.page_handle
        for a in existing_assignments
    )
    if is_new:
        max_assignments = _get_tier_limit(ctx.tier, "max_quick_action_assignments")
        if len(existing_assignments) >= max_assignments:
            raise HTTPException(
                status_code=403,
                detail=f"Assignment limit reached ({max_assignments} for {ctx.tier} tier).",
            )

    assignment = QuickActionPageAssignment(
        page_type=body.page_type,
        page_handle=body.page_handle,
        slot_1_action_id=body.slot_1_action_id,
        slot_2_action_id=body.slot_2_action_id,
    )

    assignment_dict = assignment.model_dump()
    await repo.upsert_page_assignment(ctx.tenant_id, assignment_dict)

    logger.info(
        "Page assignment upserted: tenant=%s page_type=%s page_handle=%s",
        ctx.tenant_id[:8], body.page_type, body.page_handle or "(all)",
    )
    return _enrich_assignment(assignment_dict, actions)


# ---------------------------------------------------------------------------
# DELETE /api/admin/quick-actions/assignments/{page_type} — Delete assignment
# ---------------------------------------------------------------------------


@router.delete(
    "/assignments/{page_type}",
    status_code=204,
    summary="Delete a page assignment",
    description="Removes the quick action assignment for a page type.",
    responses={
        404: {"description": "Assignment not found"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def delete_page_assignment(
    page_type: str,
    page_handle: str | None = Query(
        None, description="Page handle for specific page match",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete a page assignment."""
    repo = _get_repo()
    removed = await repo.delete_page_assignment(
        ctx.tenant_id, page_type, page_handle,
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Assignment not found")

    logger.info(
        "Page assignment deleted: tenant=%s page_type=%s page_handle=%s",
        ctx.tenant_id[:8], page_type, page_handle or "(all)",
    )


# ---------------------------------------------------------------------------
# GET /api/admin/quick-actions/{action_id} — Get single prompt
# ---------------------------------------------------------------------------


@router.get(
    "/{action_id}",
    response_model=QuickActionResponse,
    summary="Get a quick action prompt",
    responses={
        404: {"description": "Quick action not found"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def get_quick_action(
    action_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> QuickActionResponse:
    """Get a single quick action prompt by ID."""
    repo = _get_repo()
    actions = await repo.get_quick_actions(ctx.tenant_id)
    action = _find_action_by_id(actions, action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Quick action not found")

    return _action_dict_to_response(action)


# ---------------------------------------------------------------------------
# PUT /api/admin/quick-actions/{action_id} — Update prompt
# ---------------------------------------------------------------------------


@router.put(
    "/{action_id}",
    response_model=QuickActionResponse,
    summary="Update a quick action prompt",
    responses={
        404: {"description": "Quick action not found"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def update_quick_action(
    action_id: str,
    body: UpdateQuickActionRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> QuickActionResponse:
    """Update an existing quick action prompt."""
    repo = _get_repo()
    actions = await repo.get_quick_actions(ctx.tenant_id)
    action = _find_action_by_id(actions, action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Quick action not found")

    # Apply partial update
    now = datetime.now(timezone.utc).isoformat()
    if body.label is not None:
        action["label"] = body.label
    if body.prompt_template is not None:
        action["prompt_template"] = body.prompt_template
    if body.icon is not None:
        action["icon"] = body.icon
    if body.is_active is not None:
        action["is_active"] = body.is_active
    if body.sort_order is not None:
        action["sort_order"] = body.sort_order
    action["updated_at"] = now

    await repo.upsert_quick_action(ctx.tenant_id, action)

    logger.info(
        "Quick action updated: tenant=%s id=%s",
        ctx.tenant_id[:8], action_id[:8],
    )
    return _action_dict_to_response(action)


# ---------------------------------------------------------------------------
# DELETE /api/admin/quick-actions/{action_id} — Delete prompt
# ---------------------------------------------------------------------------


@router.delete(
    "/{action_id}",
    status_code=204,
    summary="Delete a quick action prompt",
    description="Deletes a quick action and removes it from any page assignments.",
    responses={
        404: {"description": "Quick action not found"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def delete_quick_action(
    action_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete a quick action prompt and clean up assignments."""
    repo = _get_repo()
    removed = await repo.delete_quick_action(ctx.tenant_id, action_id)

    if not removed:
        raise HTTPException(status_code=404, detail="Quick action not found")

    logger.info(
        "Quick action deleted: tenant=%s id=%s",
        ctx.tenant_id[:8], action_id[:8],
    )
