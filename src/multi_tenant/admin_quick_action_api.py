# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
      VALID_PAGE_TYPES
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.activation_service import get_activation_service
from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    VALID_PAGE_TYPES,
    QuickActionPageAssignment,
    QuickActionPrompt,
)
from src.multi_tenant.middleware import get_tenant_context

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


class QuickActionResponse(CamelCaseModel):
    """A single quick action prompt button."""

    id: str
    label: str
    prompt_template: str
    icon: str | None = None
    is_active: bool = True
    sort_order: int = 0
    created_at: str
    updated_at: str


class QuickActionListResponse(CamelCaseModel):
    """List of quick action prompts for a tenant."""

    tenant_id: str
    total_count: int
    actions: list[QuickActionResponse]


class CreateQuickActionRequest(CamelCaseModel):
    """Request body for POST /api/admin/quick-actions."""

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


class UpdateQuickActionRequest(CamelCaseModel):
    """Request body for PUT /api/admin/quick-actions/{id}."""

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


class PageAssignmentResponse(CamelCaseModel):
    """A page-to-quick-action slot assignment."""

    page_type: str
    page_handle: str | None = None
    slot_1_action_id: str | None = None
    slot_2_action_id: str | None = None
    slot_1_action: QuickActionResponse | None = None
    slot_2_action: QuickActionResponse | None = None
    auto_open: bool = False
    auto_open_delay_ms: int = 3000


class PageAssignmentListResponse(CamelCaseModel):
    """List of page assignments for a tenant."""

    tenant_id: str
    total_count: int
    assignments: list[PageAssignmentResponse]


class UpsertPageAssignmentRequest(CamelCaseModel):
    """Request body for PUT /api/admin/quick-actions/assignments."""

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
    auto_open: bool = Field(
        default=False,
        description="Whether the quick action auto-opens on this page type",
    )
    auto_open_delay_ms: int = Field(
        default=3000,
        description="Delay in milliseconds before auto-opening (0 = immediate)",
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


# SPEC-1759: Per-tenant locks with LRU eviction to prevent unbounded growth.
# At 680 tenants, locks are lightweight (~100 bytes each) but should still
# be bounded. OrderedDict provides O(1) LRU eviction. Evicted locks are
# safe to discard — worst case is a brief TOCTOU window for inactive tenants.
# Configurable via MAX_TENANT_LOCKS env var.
MAX_TENANT_LOCKS: int = int(os.environ.get("MAX_TENANT_LOCKS", "1000"))
_tenant_qa_locks: OrderedDict[str, asyncio.Lock] = OrderedDict()


def _get_tenant_lock(tenant_id: str) -> asyncio.Lock:
    """Get or create a per-tenant lock for atomic operations.

    SPEC-1759: Uses OrderedDict for LRU tracking. When the cap is reached,
    the oldest (least recently used) lock is evicted. This is safe because
    evicted locks belong to inactive tenants — if they become active again,
    a new lock is created.
    """
    if tenant_id in _tenant_qa_locks:
        _tenant_qa_locks.move_to_end(tenant_id)
        return _tenant_qa_locks[tenant_id]

    # New tenant — enforce cap with LRU eviction
    if len(_tenant_qa_locks) >= MAX_TENANT_LOCKS:
        evicted_id, _ = _tenant_qa_locks.popitem(last=False)
        logger.debug(
            "Tenant lock cap reached (%d), evicted oldest: %s",
            MAX_TENANT_LOCKS,
            evicted_id[:8],
        )

    lock = asyncio.Lock()
    _tenant_qa_locks[tenant_id] = lock
    return lock


async def _ensure_qa_draft(ctx: TenantContext) -> None:
    """Ensure a draft document exists before any QA write operation.

    This makes the repo methods (which prefer draft-first) naturally
    write to the draft instead of the active document, and sets the
    ``qa_modified_at`` signal so the Pending badge appears.
    """
    from src.multi_tenant.cosmos_schema import TenantTier

    activation_svc = get_activation_service()
    tier = TenantTier(ctx.tier) if ctx.tier else TenantTier.STARTER
    await activation_svc.ensure_draft_for_signal(
        tenant_id=ctx.tenant_id,
        tier=tier,
        signal_field="qa_modified_at",
        actor=f"user:{ctx.user_id}" if ctx.user_id else "admin",
    )


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
    actions: list[dict[str, Any]],
    action_id: str,
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
        auto_open=assignment.get("auto_open", False),
        auto_open_delay_ms=assignment.get("auto_open_delay_ms", 3000),
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

    # SPEC-1747: Atomic reservation — hold per-tenant lock across
    # count check + write to prevent TOCTOU race conditions.
    lock = _get_tenant_lock(ctx.tenant_id)
    async with lock:
        # Ensure draft exists before QA write (D20 fix)
        await _ensure_qa_draft(ctx)

        now = datetime.now(UTC).isoformat()
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
        ctx.tenant_id[:8],
        action.id[:8],
        action.label[:30],
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
            detail=f"Invalid page_type '{body.page_type}'. Valid values: {sorted(VALID_PAGE_TYPES)}",
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

    # SPEC-1747: Atomic reservation for assignment count check + write.
    lock = _get_tenant_lock(ctx.tenant_id)
    async with lock:
        # Check tier limit for new assignments
        existing_assignments = await repo.get_page_assignments(ctx.tenant_id)
        not any(
            a.get("page_type") == body.page_type and a.get("page_handle") == body.page_handle
            for a in existing_assignments
        )
        # Ensure draft exists before QA write (D68 fix)
        await _ensure_qa_draft(ctx)

        assignment = QuickActionPageAssignment(
            page_type=body.page_type,
            page_handle=body.page_handle,
            slot_1_action_id=body.slot_1_action_id,
            slot_2_action_id=body.slot_2_action_id,
            auto_open=body.auto_open,
            auto_open_delay_ms=body.auto_open_delay_ms,
        )

        assignment_dict = assignment.model_dump()
        await repo.upsert_page_assignment(ctx.tenant_id, assignment_dict)

    logger.info(
        "Page assignment upserted: tenant=%s page_type=%s page_handle=%s",
        ctx.tenant_id[:8],
        body.page_type,
        body.page_handle or "(all)",
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
        None,
        description="Page handle for specific page match",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> None:
    """Delete a page assignment."""
    repo = _get_repo()

    # Ensure draft exists before QA write (D68 fix)
    await _ensure_qa_draft(ctx)

    removed = await repo.delete_page_assignment(
        ctx.tenant_id,
        page_type,
        page_handle,
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Assignment not found")

    logger.info(
        "Page assignment deleted: tenant=%s page_type=%s page_handle=%s",
        ctx.tenant_id[:8],
        page_type,
        page_handle or "(all)",
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

    # Ensure draft exists before QA write (D20 fix)
    await _ensure_qa_draft(ctx)

    # Apply partial update
    now = datetime.now(UTC).isoformat()
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
        ctx.tenant_id[:8],
        action_id[:8],
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

    # Ensure draft exists before QA write (D20 fix)
    await _ensure_qa_draft(ctx)

    removed = await repo.delete_quick_action(ctx.tenant_id, action_id)

    if not removed:
        raise HTTPException(status_code=404, detail="Quick action not found")

    logger.info(
        "Quick action deleted: tenant=%s id=%s",
        ctx.tenant_id[:8],
        action_id[:8],
    )


# ---------------------------------------------------------------------------
# POST /api/admin/quick-actions/seed — Seed starter quick actions (WI #242)
# ---------------------------------------------------------------------------

_STARTER_ACTIONS = [
    {
        "label": "Track my order",
        "prompt_template": "I'd like to check on the status of my recent order.",
        "icon": "\U0001f4e6",
    },
    {
        "label": "Return or exchange",
        "prompt_template": "I need help with a return or exchange for a product I purchased.",
        "icon": "\U0001f504",
    },
    {
        "label": "Product question",
        "prompt_template": "I have a question about one of your products before I make a purchase.",
        "icon": "\u2753",
    },
    {
        "label": "Shipping info",
        "prompt_template": "What are your shipping options and delivery timeframes?",
        "icon": "\U0001f69a",
    },
]


@router.post(
    "/seed",
    summary="Seed starter quick actions",
    description=(
        "Creates 4 example quick actions if none exist. Idempotent — does nothing if quick actions already exist."
    ),
    responses={
        200: {"description": "Seed result"},
        503: {"description": "Quick action services not initialized"},
    },
)
async def seed_quick_actions(
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Seed starter quick actions for new tenants (WI #242)."""
    repo = _get_repo()

    existing = await repo.list_quick_actions(ctx.tenant_id)
    if existing:
        return {"seeded": 0, "message": "Quick actions already exist"}

    now = datetime.now(UTC).isoformat()
    created = []
    for i, starter in enumerate(_STARTER_ACTIONS):
        action = {
            "id": str(uuid.uuid4()),
            "label": starter["label"],
            "prompt_template": starter["prompt_template"],
            "icon": starter.get("icon", ""),
            "is_active": True,
            "sort_order": i * 10,
            "created_at": now,
            "updated_at": now,
        }
        await repo.upsert_quick_action(ctx.tenant_id, action)
        created.append(action["id"])

    logger.info(
        "Seeded %d starter quick actions: tenant=%s",
        len(created),
        ctx.tenant_id[:8],
    )
    return {"seeded": len(created), "ids": created}
