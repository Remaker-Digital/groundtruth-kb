"""Implementation for the governed ``gt backlog add`` command.

Authority: bridge/gtkb-backlog-add-cli-slice-1-003.md (REVISED-1), Codex GO at
``bridge/gtkb-backlog-add-cli-slice-1-004.md``. Source work item: WI-3270.

``gt backlog add`` (and ``python -m groundtruth_kb backlog add`` parity)
captures a single MemBase ``work_items`` candidate row per invocation so that
agents can record noticed issues or enhancement opportunities during normal
work without parking them in ``memory/MEMORY.md`` or ``memory/work_list.md``.

Capture is NOT implementation approval. The new row records a candidate for
future implementation consideration; implementing the captured item still
requires a normal bridge proposal, Loyal Opposition ``GO``, and (where
applicable) project authorization or per-artifact owner approval.

Attribution: this module is a mutating MemBase writer. Per the verified
harness-aware attribution contract (``bridge/gtkb-kb-attribution-harness-aware-003.md``,
Codex GO at ``-004``), it resolves ``changed_by`` exclusively through the
MUTATING ``scripts._kb_attribution.resolve_changed_by()`` resolver, which
raises ``RuntimeError`` when no harness can be resolved. No ``--changed-by``
option, environment override, or fallback literal may ever write a row
(GO Implementation Conditions 1 and 2).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB

# The attribution resolver lives under ``scripts/`` at the project root, which
# is not on ``sys.path`` when ``groundtruth_kb`` is imported as an installed
# package. Make ``scripts._kb_attribution`` importable by adding the project
# root (three parents up from ``groundtruth-kb/src/groundtruth_kb/``).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class BacklogAddError(Exception):
    """Raised when ``gt backlog add`` cannot safely proceed."""


# Allowed origin values for a captured backlog candidate. Single source of
# truth for both the CLI ``click.Choice`` and the deterministic validation
# here (REVISED-1 § Risks and Rollback, Risk 2).
BACKLOG_ADD_ORIGINS = ("new", "hygiene", "improvement", "defect", "regression")

# Allowed priority values; ``P3`` is the low-ceremony candidate default.
BACKLOG_ADD_PRIORITIES = ("P0", "P1", "P2", "P3")
_DEFAULT_PRIORITY = "P3"

# Fail-closed attribution: these literals must NEVER reach a ``work_items``
# row (GO Implementation Condition 2). They exist only as a guard set so the
# regression test ``test_add_does_not_emit_fallback_changed_by`` can assert
# their absence.
_FORBIDDEN_CHANGED_BY = ("gt-backlog-add", "unknown", "prime-builder/unknown")


@dataclass(frozen=True)
class BacklogAddRequest:
    """Validated request for a single ``gt backlog add`` invocation.

    There is intentionally no ``changed_by`` / ``changed_by_override`` field
    (REVISED-1 IP-3): attribution is resolved fail-closed by the resolver,
    never supplied by the caller.
    """

    title: str
    origin: str
    component: str
    priority: str | None
    project_name: str | None
    subproject_name: str | None
    description: str | None
    source_owner_directive: str | None
    source_spec_id: str | None
    source_deliberation_query: str | None
    related_spec_ids_at_creation: str | None
    related_deliberation_ids: str | None
    related_bridge_threads: str | None
    depends_on_work_items: str | None
    acceptance_summary: str | None
    regression_visibility: str | None
    change_reason: str
    dry_run: bool


def _validate_request(request: BacklogAddRequest) -> str:
    """Validate required + enum fields; return the resolved priority.

    Raises:
        BacklogAddError: on any required-field or enum violation.
    """
    if not request.title or not request.title.strip():
        raise BacklogAddError("--title must be a non-empty string")
    if request.origin not in BACKLOG_ADD_ORIGINS:
        allowed = ", ".join(BACKLOG_ADD_ORIGINS)
        raise BacklogAddError(f"--origin must be one of: {allowed}")
    if not request.component or not request.component.strip():
        raise BacklogAddError("--component must be a non-empty string")
    if not request.change_reason or not request.change_reason.strip():
        raise BacklogAddError("--change-reason must be a non-empty string")

    priority = request.priority if request.priority is not None else _DEFAULT_PRIORITY
    if priority not in BACKLOG_ADD_PRIORITIES:
        allowed = ", ".join(BACKLOG_ADD_PRIORITIES)
        raise BacklogAddError(f"--priority must be one of: {allowed}")
    return priority


def _resolve_changed_by() -> str:
    """Resolve ``changed_by`` via the MUTATING fail-closed resolver.

    Raises:
        RuntimeError: surfaced unchanged from
            ``scripts._kb_attribution.resolve_changed_by()`` when no harness
            can be resolved. The caller MUST surface this as a non-zero exit
            BEFORE any ``insert_work_item`` call (GO Implementation
            Condition 1).
    """
    # Local import so a resolver-module signature change fails loud (at call
    # time) rather than at module import time, and to keep the attribution
    # surface explicit.
    from scripts._kb_attribution import resolve_changed_by

    return resolve_changed_by()


def _allocate_next_work_item_id(db: KnowledgeDB) -> str:
    """Allocate the next monotonic ``WI-NNNN`` id.

    Scans existing ``work_items`` rows for the maximum ``WI-<n>`` numeric
    suffix and returns ``WI-<n+1>``. When no ``WI-`` rows exist, starts at
    ``WI-0001``. The SELECT and the subsequent INSERT run in the same
    connection; the residual concurrent-allocation race is mitigated by the
    duplicate-id guard in :func:`add_backlog_item` and documented as a Slice 1
    follow-on (REVISED-1 § Risks and Rollback, Risk 1).
    """
    rows = db._get_conn().execute("SELECT id FROM work_items").fetchall()
    max_n = 0
    for row in rows:
        item_id = row[0]
        if not isinstance(item_id, str) or not item_id.startswith("WI-"):
            continue
        suffix = item_id[3:]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return f"WI-{max_n + 1:04d}"


def add_backlog_item(config: GTConfig, request: BacklogAddRequest) -> dict[str, Any]:
    """Validate, allocate an id, and insert one ``work_items`` candidate row.

    On ``request.dry_run`` the allocated id and insert kwargs are returned
    without writing. Otherwise a single ``insert_work_item`` call persists the
    row with ``resolution_status='open'`` and ``stage='backlogged'``.

    Raises:
        BacklogAddError: on field validation failure or duplicate-id collision.
        RuntimeError: when harness attribution cannot be resolved (surfaced
            unchanged from the resolver, before any DB write).
    """
    priority = _validate_request(request)

    # Attribution is resolved BEFORE opening any write path. A RuntimeError
    # here propagates to the caller, which exits non-zero with no DB mutation.
    changed_by = _resolve_changed_by()

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)

    allocated_id = _allocate_next_work_item_id(db)
    if db.get_work_item(allocated_id) is not None:
        raise BacklogAddError(
            f"allocated id {allocated_id} already exists; refusing to overwrite "
            "(allocation race — retry the command)"
        )

    insert_kwargs: dict[str, Any] = {
        "id": allocated_id,
        "title": request.title,
        "origin": request.origin,
        "component": request.component,
        "resolution_status": "open",
        "changed_by": changed_by,
        "change_reason": request.change_reason,
        "description": request.description,
        "source_spec_id": request.source_spec_id,
        "priority": priority,
        "stage": "backlogged",
        "project_name": request.project_name,
        "subproject_name": request.subproject_name,
        "source_owner_directive": request.source_owner_directive,
        "source_deliberation_query": request.source_deliberation_query,
        "related_deliberation_ids": request.related_deliberation_ids,
        "related_spec_ids_at_creation": request.related_spec_ids_at_creation,
        "related_bridge_threads": request.related_bridge_threads,
        "depends_on_work_items": request.depends_on_work_items,
        "acceptance_summary": request.acceptance_summary,
        "regression_visibility": request.regression_visibility,
    }

    if request.dry_run:
        return {
            "created": False,
            "dry_run": True,
            "id": allocated_id,
            "kwargs": insert_kwargs,
        }

    row = db.insert_work_item(**insert_kwargs)
    if row is None:
        raise BacklogAddError(
            f"Unexpected error: inserted work item {allocated_id} not found on readback."
        )

    return {
        "created": True,
        "dry_run": False,
        "id": row["id"],
        "row": row,
    }
