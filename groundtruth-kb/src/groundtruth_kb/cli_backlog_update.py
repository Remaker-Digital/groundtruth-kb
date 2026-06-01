"""Implementation for the governed ``gt backlog update`` and ``gt backlog resolve`` commands.

Authority: bridge/gtkb-backlog-update-cli-slice-1-003.md (REVISED-1), Codex GO at
``bridge/gtkb-backlog-update-cli-slice-1-004.md``. Source work item: WI-3436.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB

# The attribution resolver lives under ``scripts/`` at the project root.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class BacklogUpdateError(Exception):
    """Raised when ``gt backlog update`` cannot safely proceed."""


@dataclass(frozen=True)
class BacklogUpdateRequest:
    """Validated request for a single ``gt backlog update`` invocation."""

    work_item_id: str
    resolution_status: str | None
    stage: str | None
    priority: str | None
    related_bridge_threads: str | None
    status_detail: str | None
    owner_approved: bool
    change_reason: str
    dry_run: bool


def _resolve_changed_by() -> str:
    """Resolve ``changed_by`` via the MUTATING fail-closed resolver."""
    from scripts._kb_attribution import resolve_changed_by

    return resolve_changed_by()


def update_backlog_item(config: GTConfig, request: BacklogUpdateRequest) -> dict[str, Any]:
    """Validate, verify GOV-15 authorization, and update a work item row.

    On ``request.dry_run`` the updated fields are validated and reported
    without writing. Otherwise a single ``update_work_item`` call persists the
    new version.
    """
    if not request.work_item_id or not request.work_item_id.strip():
        raise BacklogUpdateError("Work item ID must be specified")
    if not request.change_reason or not request.change_reason.strip():
        raise BacklogUpdateError("--change-reason must be a non-empty string")

    # Validate vocabulary
    VALID_STATUSES = {
        "new",
        "open",
        "unresolved",
        "in_progress",
        "resolved",
        "verified",
        "retired",
        "wont_fix",
        "not_a_defect",
    }
    if request.resolution_status is not None and request.resolution_status not in VALID_STATUSES:
        allowed = ", ".join(sorted(VALID_STATUSES))
        raise BacklogUpdateError(f"Invalid resolution status '{request.resolution_status}'. Allowed: {allowed}")

    VALID_STAGES = {"created", "tested", "backlogged", "implementing", "resolved"}
    if request.stage is not None and request.stage not in VALID_STAGES:
        allowed = ", ".join(sorted(VALID_STAGES))
        raise BacklogUpdateError(f"Invalid stage '{request.stage}'. Allowed: {allowed}")

    if request.priority is not None and request.priority not in {"P0", "P1", "P2", "P3"}:
        raise BacklogUpdateError("Invalid priority. Allowed: P0, P1, P2, P3")

    # Attribution is resolved BEFORE opening any write path
    changed_by = _resolve_changed_by()

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    current = db.get_work_item(request.work_item_id)
    if not current:
        raise BacklogUpdateError(f"Work item {request.work_item_id} not found")

    current_status = current.get("resolution_status")
    new_status = request.resolution_status if request.resolution_status is not None else current_status

    # GOV-15 CLI-layer check for terminal resolution transition on defect/regression
    TERMINAL_STATUSES = {"resolved", "verified", "retired", "wont_fix", "not_a_defect"}
    is_terminal_transition = new_status in TERMINAL_STATUSES and current_status not in TERMINAL_STATUSES

    if is_terminal_transition and current.get("origin") in {"defect", "regression"} and not request.owner_approved:
        raise BacklogUpdateError(
            f"Cannot resolve defect/regression work item {request.work_item_id} "
            f"without explicit owner approval (--owner-approved required under GOV-15)."
        )

    fields: dict[str, Any] = {}
    if request.resolution_status is not None:
        fields["resolution_status"] = request.resolution_status
    if request.stage is not None:
        fields["stage"] = request.stage
    if request.priority is not None:
        fields["priority"] = request.priority
    if request.related_bridge_threads is not None:
        fields["related_bridge_threads"] = request.related_bridge_threads
    if request.status_detail is not None:
        fields["status_detail"] = request.status_detail

    # Test the stage transition against the database logic
    current_stage = current.get("stage", "created")
    new_stage = request.stage if request.stage is not None else current_stage
    try:
        db._validate_stage_transition(
            request.work_item_id,
            current_stage,
            new_stage,
            owner_approved=request.owner_approved,
        )
    except ValueError as exc:
        raise BacklogUpdateError(str(exc)) from exc

    if request.dry_run:
        return {
            "updated": False,
            "dry_run": True,
            "work_item_id": request.work_item_id,
            "fields": fields,
        }

    try:
        row = db.update_work_item(
            request.work_item_id,
            changed_by,
            request.change_reason,
            owner_approved=request.owner_approved,
            **fields,
        )
    except ValueError as exc:
        raise BacklogUpdateError(str(exc)) from exc

    if row is None:
        raise BacklogUpdateError(f"Unexpected error: updated work item {request.work_item_id} not found on readback.")

    return {
        "updated": True,
        "dry_run": False,
        "work_item_id": row["id"],
        "row": row,
    }
