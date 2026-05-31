"""Implementation for the governed ``gt backlog add-work-item`` command.

Authority: bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-005.md
(REVISED-2), Codex GO at ``-006.md``. Source work item: WI-3455. Project
authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-3-
KB-WORK-ITEM-MIGRATION (v2).

``gt backlog add-work-item`` is the deterministic service for the full GOV-12
(work item triggers a linked test) + GOV-13 (every test assigned to a test-plan
phase at creation) chain that the ``kb-work-item`` skill previously performed
through inline ``db.insert_*`` snippets in skill markdown (the
``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` anti-pattern). The skill becomes
a thin wrapper around this verb.

GOV-13 is enforced fail-closed: ``--test-plan-phase`` is REQUIRED for non-dry-run
creation and is validated to resolve to a current ``test_plan_phases`` row before
any work-item/test/phase mutation. No code path creates a test without assigning
it to a phase. The phase id is a required parameter (caller-supplied); this verb
hardcodes no application-specific phase taxonomy (the Agent-Red ``kb-work-item``
skill supplies the ``PLAN-001`` phase), preserving platform/application isolation
per ``ADR-ISOLATION-APPLICATION-PLACEMENT-001``.

Attribution: this module reuses the fail-closed mutating attribution resolver
(``scripts._kb_attribution.resolve_changed_by``) for the test + phase writes,
and delegates the work-item write to ``cli_backlog_add.add_backlog_item`` which
resolves attribution the same way. No ``--changed-by`` option, environment
override, or fallback literal may ever write a row.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB

# ``scripts._kb_attribution`` lives at the project root, not on ``sys.path``
# when ``groundtruth_kb`` is imported as an installed package.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class AddWorkItemError(Exception):
    """Raised when ``gt backlog add-work-item`` cannot safely proceed."""


# GOV-12 test types (single source of truth for the click.Choice + validation).
TEST_TYPES = ("assertion", "e2e", "integration", "unit", "manual")


@dataclass(frozen=True)
class AddWorkItemRequest:
    """Validated request for one ``gt backlog add-work-item`` invocation.

    Work-item fields mirror ``BacklogAddRequest``; the ``test_*`` fields drive
    the GOV-12 linked-test creation and ``test_plan_phase`` drives the
    REQUIRED GOV-13 phase assignment. There is intentionally no ``changed_by``
    field — attribution is resolved fail-closed, never caller-supplied.
    """

    # Work item (GOV-12 trigger)
    title: str
    origin: str
    component: str
    priority: str | None
    project_name: str | None
    subproject_name: str | None
    description: str | None
    source_owner_directive: str | None
    source_spec_id: str | None
    change_reason: str
    # Linked test (GOV-12)
    test_title: str
    test_type: str
    test_expected_outcome: str
    test_spec_id: str | None  # defaults to source_spec_id when None
    # Phase assignment (GOV-13) — REQUIRED for non-dry-run
    test_plan_phase: str | None
    dry_run: bool


def _resolve_changed_by() -> str:
    """Resolve ``changed_by`` via the MUTATING fail-closed resolver.

    Raises ``RuntimeError`` (surfaced unchanged) when no harness can be
    resolved. The caller MUST surface this as a non-zero exit BEFORE any
    work-item/test/phase write.
    """
    from scripts._kb_attribution import resolve_changed_by

    return resolve_changed_by()


def _coerce_test_ids(raw: Any) -> list[str]:
    """Return a phase's ``test_ids`` as a list.

    ``get_test_plan_phase`` may return ``test_ids`` as a JSON string (the
    stored form) rather than a parsed list; coerce both forms (and ``None``)
    to a list so appends never char-split an existing JSON string.
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = raw.strip()
        return list(json.loads(raw)) if raw else []
    return list(raw)


def _allocate_next_test_id(db: KnowledgeDB) -> str:
    """Allocate the next monotonic ``TEST-NNNN`` id.

    Mirrors the work-item allocator in :mod:`cli_backlog_add`: scans existing
    ``tests`` rows for the maximum ``TEST-<n>`` numeric suffix and returns
    ``TEST-<n+1>`` (zero-padded to 4), starting at ``TEST-0001``.
    """
    rows = db._get_conn().execute("SELECT id FROM tests").fetchall()
    max_n = 0
    for row in rows:
        test_id = row[0]
        if not isinstance(test_id, str) or not test_id.startswith("TEST-"):
            continue
        suffix = test_id[5:]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return f"TEST-{max_n + 1:04d}"


def _validate_request(request: AddWorkItemRequest) -> str:
    """Validate the test/phase fields specific to this verb.

    Work-item-field validation is delegated to ``BacklogAddRequest`` /
    ``add_backlog_item``. This function validates the GOV-12 test fields and the
    GOV-13 phase requirement (fail-closed). Returns the resolved test spec id.

    Raises:
        AddWorkItemError: on any test/phase validation failure.
    """
    if not request.test_title or not request.test_title.strip():
        raise AddWorkItemError("--test-title must be a non-empty string (GOV-12)")
    if request.test_type not in TEST_TYPES:
        raise AddWorkItemError(f"--test-type must be one of: {', '.join(TEST_TYPES)}")
    if not request.test_expected_outcome or not request.test_expected_outcome.strip():
        raise AddWorkItemError("--test-expected-outcome must be a non-empty string (GOV-03)")

    test_spec_id = request.test_spec_id or request.source_spec_id
    if not test_spec_id or not test_spec_id.strip():
        raise AddWorkItemError("a test spec is required (GOV-12): pass --test-spec-id or --source-spec-id")

    # GOV-13 fail-closed: a phase is required for real (non-dry-run) creation.
    if not request.dry_run and (not request.test_plan_phase or not request.test_plan_phase.strip()):
        raise AddWorkItemError(
            "--test-plan-phase is required (GOV-13: every test must be assigned to a "
            "test-plan phase at creation). No work item or test was created."
        )
    return test_spec_id


def add_work_item_with_test(config: GTConfig, request: AddWorkItemRequest) -> dict[str, Any]:
    """Create a work item + linked test + phase assignment in one invocation.

    Fail-closed order (no orphan work item or test is ever persisted on a
    validation failure):

    1. Validate test/phase fields (raises before any write).
    2. Resolve attribution (raises before any write).
    3. Validate the ``--test-plan-phase`` resolves to a current phase (raises
       before any write); skipped on dry-run after step 1's presence check.
    4. Create the work item (delegated to ``add_backlog_item``).
    5. Create the linked test (GOV-12).
    6. Append the test id to the phase's ``test_ids`` (GOV-13, append-only).

    Returns a dict with ``work_item_id``, ``test_id``, ``phase_id``, and
    ``dry_run``.
    """
    from groundtruth_kb.cli_backlog_add import BacklogAddError, BacklogAddRequest, add_backlog_item

    test_spec_id = _validate_request(request)

    # Attribution resolved BEFORE any write path (fail-closed). A RuntimeError
    # propagates to the caller, which exits non-zero with no DB mutation.
    changed_by = _resolve_changed_by()

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)

    # GOV-13 fail-closed: the phase must exist before we create anything, so the
    # later append cannot fail on a missing phase (no orphan-test window).
    phase = None
    if request.test_plan_phase:
        phase = db.get_test_plan_phase(request.test_plan_phase)
        if phase is None:
            raise AddWorkItemError(
                f"--test-plan-phase {request.test_plan_phase!r} does not resolve to a current "
                "test_plan_phases row (GOV-13). No work item or test was created."
            )

    wi_request = BacklogAddRequest(
        title=request.title,
        origin=request.origin,
        component=request.component,
        priority=request.priority,
        project_name=request.project_name,
        subproject_name=request.subproject_name,
        description=request.description,
        source_owner_directive=request.source_owner_directive,
        source_spec_id=request.source_spec_id,
        source_deliberation_query=None,
        related_spec_ids_at_creation=None,
        related_deliberation_ids=None,
        related_bridge_threads=None,
        depends_on_work_items=None,
        acceptance_summary=None,
        regression_visibility=None,
        change_reason=request.change_reason,
        dry_run=request.dry_run,
    )

    if request.dry_run:
        try:
            wi_result = add_backlog_item(config, wi_request)
        except (BacklogAddError, RuntimeError) as exc:
            raise AddWorkItemError(str(exc)) from exc
        return {
            "created": False,
            "dry_run": True,
            "work_item_id": wi_result["id"],
            "test_id": _allocate_next_test_id(db),
            "phase_id": request.test_plan_phase,
        }

    # --- Non-dry-run: create work item, then test, then assign to phase. ---
    try:
        wi_result = add_backlog_item(config, wi_request)
    except (BacklogAddError, RuntimeError) as exc:
        raise AddWorkItemError(str(exc)) from exc
    work_item_id = wi_result["id"]

    test_id = _allocate_next_test_id(db)
    test_row = db.insert_test(
        id=test_id,
        title=request.test_title,
        spec_id=test_spec_id,
        test_type=request.test_type,
        expected_outcome=request.test_expected_outcome,
        changed_by=changed_by,
        change_reason=f"GOV-12: linked test for {work_item_id} ({request.change_reason})",
        description=f"Auto-created with {work_item_id} via gt backlog add-work-item.",
    )
    if test_row is None:
        raise AddWorkItemError(f"insert_test for {test_id} returned None on readback.")

    # GOV-13: append the test id to the phase's test_ids (append-only new version).
    assert phase is not None  # guaranteed by the fail-closed validation above
    existing_ids = _coerce_test_ids(phase.get("test_ids"))
    if test_id not in existing_ids:
        existing_ids.append(test_id)
    phase_row = db.insert_test_plan_phase(
        id=phase["id"],
        plan_id=phase["plan_id"],
        phase_order=phase["phase_order"],
        title=phase["title"],
        gate_criteria=phase["gate_criteria"],
        changed_by=changed_by,
        change_reason=f"GOV-13: assign {test_id} to phase {phase['id']} (with {work_item_id})",
        description=phase.get("description"),
        test_ids=existing_ids,
        last_result=phase.get("last_result"),
        last_executed_at=phase.get("last_executed_at"),
    )
    if phase_row is None:
        raise AddWorkItemError(f"insert_test_plan_phase for {phase['id']} returned None on readback.")

    return {
        "created": True,
        "dry_run": False,
        "work_item_id": work_item_id,
        "test_id": test_id,
        "phase_id": phase["id"],
    }
