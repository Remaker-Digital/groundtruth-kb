"""Implementation for the governed ``gt backlog update`` and ``gt backlog resolve`` commands.

Authority: bridge/gtkb-backlog-update-cli-slice-1-003.md (REVISED-1), Codex GO at
``bridge/gtkb-backlog-update-cli-slice-1-004.md``. Source work item: WI-3436.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService

LOGGER = logging.getLogger(__name__)

# The attribution resolver lives under ``scripts/`` at the project root.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Canonical authorization-token shapes for the disjunctive text-edit gate.
# Authority: bridge/gtkb-backlog-update-title-desc-cli-001-003.md REVISED-1
# GO at bridge/gtkb-backlog-update-title-desc-cli-001-004.md (WI-4357).
_PAUTH_TOKEN_RE = re.compile(r"\bPAUTH-[A-Z0-9][A-Z0-9-]*\b")
_DELIB_TOKEN_RE = re.compile(r"\bDELIB-[A-Z0-9][A-Z0-9-]*\b")


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
    title: str | None = None
    description: str | None = None
    source_spec_id: str | None = None


def _resolve_changed_by() -> str:
    """Resolve ``changed_by`` via the MUTATING fail-closed resolver."""
    from scripts._kb_attribution import resolve_changed_by  # type: ignore[import-untyped]

    return cast(str, resolve_changed_by())


def _validate_json_string_array(value: str | None, option_name: str) -> None:
    """Reject malformed structured link values before any DB write."""
    if value is None:
        return
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise BacklogUpdateError(f"{option_name} is invalid: expected a JSON array of strings") from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise BacklogUpdateError(f"{option_name} is invalid: expected a JSON array of strings")


def _verify_text_edit_gate(db: KnowledgeDB, current: dict[str, Any], request: BacklogUpdateRequest) -> None:
    """Enforce the disjunctive text-edit gate for ``--title`` / ``--description``.

    Raises ``BacklogUpdateError`` if none of the three disjunctive arms is
    satisfied. The arms are:

    1. ``current['approval_state'] == 'bridge_authorized'``
    2. ``request.owner_approved`` is True
    3. ``request.change_reason`` cites an active ``PAUTH-*`` token (verified
       against ``current_project_authorizations`` with status active) OR an
       existing ``DELIB-*`` token (verified against ``current_deliberations``).

    Substring presence is not enough: each cited token is looked up in the DB
    and rejected if the row is missing or, for PAUTH, not active.
    """
    if current.get("approval_state") == "bridge_authorized":
        return
    if request.owner_approved:
        return

    for token in _PAUTH_TOKEN_RE.findall(request.change_reason):
        record = db.get_project_authorization(token)
        if record and record.get("status") == "active":
            return

    for token in _DELIB_TOKEN_RE.findall(request.change_reason):
        if db.get_deliberation(token):
            return

    raise BacklogUpdateError(
        f"Cannot edit title or description of work item {request.work_item_id} "
        f"without text-edit authorization. Satisfy one of: (1) the work item "
        f"has approval_state=bridge_authorized; (2) pass --owner-approved; "
        f"(3) cite an active PAUTH-* token or an existing DELIB-* token in "
        f"--change-reason."
    )


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

    _validate_json_string_array(request.related_bridge_threads, "--related-bridge-threads")

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

    # Disjunctive text-edit gate: applies whenever --title or --description is
    # provided. Satisfied if any of: WI.approval_state == bridge_authorized,
    # --owner-approved is set, or --change-reason cites an existing active
    # PAUTH-* token or an existing DELIB-* token. The gate composes
    # independently with the GOV-15 terminal-resolution gate above and the
    # stage-transition gate below (see Forbidden-Field-Combination Policy in
    # bridge/gtkb-backlog-update-title-desc-cli-001-003.md).
    if request.title is not None or request.description is not None:
        _verify_text_edit_gate(db, current, request)

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
    if request.title is not None:
        fields["title"] = request.title
    if request.description is not None:
        fields["description"] = request.description
    if request.source_spec_id is not None:
        fields["source_spec_id"] = request.source_spec_id

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

    auto_retired_projects: list[dict[str, Any]] = []
    if is_terminal_transition:
        try:
            auto_retired_projects = ProjectLifecycleService(db).auto_retire_projects_for_work_item(
                request.work_item_id,
                project_root=_PROJECT_ROOT,
                changed_by=changed_by,
            )
        except Exception as exc:  # noqa: BLE001 - the work-item update already committed; actuation is best-effort.
            LOGGER.warning("Skipping automatic project retirement after %s update: %s", request.work_item_id, exc)

    return {
        "updated": True,
        "dry_run": False,
        "work_item_id": row["id"],
        "row": row,
        "auto_retired_projects": auto_retired_projects,
    }
