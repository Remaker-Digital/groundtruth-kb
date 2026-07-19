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
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

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
_CANONICAL_WORK_ITEM_ID = re.compile(r"WI-\d{4,}")
_CANONICAL_TEST_ID = re.compile(r"TEST-\d{4,}")


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


@dataclass(frozen=True)
class RepairWorkItemTestLinkRequest:
    """One exact historical work-item/test/phase repair request."""

    work_item_id: str
    test_id: str
    phase_id: str
    change_reason: str
    dry_run: bool


@dataclass(frozen=True)
class ExistingWorkItemLinkedTestRequest:
    """Create and link one test for one already-existing work item."""

    work_item_id: str
    test_title: str
    test_type: str
    test_expected_outcome: str
    test_spec_id: str | None
    phase_id: str
    change_reason: str
    dry_run: bool


def _resolve_changed_by(project_root: Path) -> str:
    """Resolve ``changed_by`` via the MUTATING fail-closed resolver.

    Raises ``RuntimeError`` (surfaced unchanged) when no harness can be
    resolved. The caller MUST surface this as a non-zero exit BEFORE any
    work-item/test/phase write.
    """
    from scripts._kb_attribution import resolve_changed_by  # type: ignore[import-untyped]

    return cast(str, resolve_changed_by(project_root=project_root))


def _coerce_test_ids(raw: Any) -> list[str]:
    """Validate and normalize one phase's canonical ``test_ids`` value."""
    if raw is None:
        return []
    if isinstance(raw, str):
        if not raw.strip():
            raise AddWorkItemError("phase test_ids must be null, a list, or a JSON-encoded list")
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AddWorkItemError("phase test_ids contains malformed JSON") from exc
    if not isinstance(raw, list):
        raise AddWorkItemError("phase test_ids must decode to a list")

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str) or not item or item != item.strip():
            raise AddWorkItemError("phase test_ids must contain non-empty canonical test-id strings")
        if _CANONICAL_TEST_ID.fullmatch(item) is None:
            raise AddWorkItemError(f"phase test_ids contains noncanonical test id {item!r}")
        if item in seen:
            raise AddWorkItemError(f"phase test_ids contains duplicate test id {item!r}")
        seen.add(item)
        normalized.append(item)
    return normalized


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

    # Dry-run and apply share the same complete preflight.
    if not request.test_plan_phase or not request.test_plan_phase.strip():
        raise AddWorkItemError(
            "--test-plan-phase is required (GOV-13: dry-run and apply must validate "
            "the exact phase used at creation). No work item or test was created."
        )
    return test_spec_id


def _work_item_request(request: AddWorkItemRequest) -> Any:
    from groundtruth_kb.cli_backlog_add import BacklogAddRequest

    return BacklogAddRequest(
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


def _preflight_add(
    db: KnowledgeDB,
    request: AddWorkItemRequest,
) -> tuple[Any, str, dict[str, Any], list[str], str, str]:
    """Run every validation and allocation used by the write path."""
    from groundtruth_kb.cli_backlog_add import (
        _allocate_next_work_item_id,
    )
    from groundtruth_kb.cli_backlog_add import (
        _validate_request as _validate_backlog_request,
    )

    test_spec_id = _validate_request(request)
    wi_request = _work_item_request(request)
    _validate_backlog_request(wi_request)

    if request.source_spec_id and db.get_spec(request.source_spec_id) is None:
        raise AddWorkItemError(f"--source-spec-id {request.source_spec_id!r} does not resolve")
    if db.get_spec(test_spec_id) is None:
        raise AddWorkItemError(f"test spec {test_spec_id!r} does not resolve")

    assert request.test_plan_phase is not None
    phase = db.get_test_plan_phase(request.test_plan_phase)
    if phase is None:
        raise AddWorkItemError(
            f"--test-plan-phase {request.test_plan_phase!r} does not resolve to a current "
            "test_plan_phases row (GOV-13). No work item or test was created."
        )
    phase_test_ids = _coerce_test_ids(phase.get("test_ids"))

    work_item_id = _allocate_next_work_item_id(db)
    test_id = _allocate_next_test_id(db)
    if db.get_work_item(work_item_id) is not None:
        raise AddWorkItemError(f"allocated work item id {work_item_id} already exists; retry")
    if db.get_test(test_id) is not None:
        raise AddWorkItemError(f"allocated test id {test_id} already exists; retry")
    return wi_request, test_spec_id, phase, phase_test_ids, work_item_id, test_id


def _commit_transaction(conn: Any) -> None:
    """Commit helper kept separate so final-commit rollback is testable."""
    conn.commit()


def add_work_item_with_test(config: GTConfig, request: AddWorkItemRequest) -> dict[str, Any]:
    """Create one linked work item, test, and phase version atomically."""
    from groundtruth_kb.cli_backlog_add import BacklogAddError, _add_backlog_item

    changed_by = _resolve_changed_by(Path(config.project_root))
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    try:
        if request.dry_run:
            _, _, phase, _, work_item_id, test_id = _preflight_add(db, request)
            return {
                "created": False,
                "dry_run": True,
                "work_item_id": work_item_id,
                "test_id": test_id,
                "phase_id": phase["id"],
            }

        conn = db._get_conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            wi_request, test_spec_id, phase, existing_ids, work_item_id, test_id = _preflight_add(db, request)
            wi_result = _add_backlog_item(
                config,
                wi_request,
                changed_by=changed_by,
                db=db,
                allocated_id=work_item_id,
                source_test_id=test_id,
                commit=False,
            )
            test_row = db.insert_test(
                id=test_id,
                title=request.test_title,
                spec_id=test_spec_id,
                test_type=request.test_type,
                expected_outcome=request.test_expected_outcome,
                changed_by=changed_by,
                change_reason=f"GOV-12: linked test for {work_item_id} ({request.change_reason})",
                description=f"Auto-created with {work_item_id} via gt backlog add-work-item.",
                commit=False,
            )
            if test_row is None:
                raise AddWorkItemError(f"insert_test for {test_id} returned None on readback.")

            phase_ids = [*existing_ids, test_id]
            phase_row = db.insert_test_plan_phase(
                id=phase["id"],
                plan_id=phase["plan_id"],
                phase_order=phase["phase_order"],
                title=phase["title"],
                gate_criteria=phase["gate_criteria"],
                changed_by=changed_by,
                change_reason=f"GOV-13: assign {test_id} to phase {phase['id']} (with {work_item_id})",
                description=phase.get("description"),
                test_ids=phase_ids,
                last_result=phase.get("last_result"),
                last_executed_at=phase.get("last_executed_at"),
                commit=False,
            )
            if phase_row is None:
                raise AddWorkItemError(f"insert_test_plan_phase for {phase['id']} returned None on readback.")

            wi_row = db.get_work_item(work_item_id)
            if wi_row is None or wi_row.get("source_test_id") != test_id:
                raise AddWorkItemError(f"work item {work_item_id} did not read back with source_test_id {test_id}")
            if wi_result["id"] != work_item_id or test_id not in _coerce_test_ids(phase_row.get("test_ids")):
                raise AddWorkItemError("atomic work-item/test/phase readback did not match the requested relationship")
            _commit_transaction(conn)
        except Exception:
            conn.rollback()
            raise

        return {
            "created": True,
            "dry_run": False,
            "work_item_id": work_item_id,
            "test_id": test_id,
            "phase_id": phase["id"],
        }
    except AddWorkItemError:
        raise
    except (BacklogAddError, RuntimeError) as exc:
        raise AddWorkItemError(str(exc)) from exc
    except Exception as exc:
        raise AddWorkItemError(f"atomic add-work-item transaction rolled back: {exc}") from exc
    finally:
        db.close()


def _linked_test_provenance(work_item_id: str) -> str:
    return f"Auto-created for {work_item_id} via gt backlog add-linked-test."


def _phase_ids_containing_test(db: KnowledgeDB, test_id: str) -> list[str]:
    rows = (
        db._get_conn()
        .execute(
            "SELECT id, test_ids FROM current_test_plan_phases WHERE test_ids LIKE ? ORDER BY id",
            (f"%{test_id}%",),
        )
        .fetchall()
    )
    return [str(row["id"]) for row in rows if test_id in _coerce_test_ids(row["test_ids"])]


def _preflight_add_linked_test(
    db: KnowledgeDB,
    request: ExistingWorkItemLinkedTestRequest,
) -> dict[str, Any]:
    """Validate one existing-WI linked-test transaction before any write."""
    if _CANONICAL_WORK_ITEM_ID.fullmatch(request.work_item_id) is None:
        raise AddWorkItemError(f"noncanonical work item id {request.work_item_id!r}")
    if not request.test_title.strip():
        raise AddWorkItemError("--test-title must be a non-empty string (GOV-12)")
    if request.test_type not in TEST_TYPES:
        raise AddWorkItemError(f"--test-type must be one of: {', '.join(TEST_TYPES)}")
    if not request.test_expected_outcome.strip():
        raise AddWorkItemError("--test-expected-outcome must be a non-empty string (GOV-03)")
    if not request.phase_id.strip():
        raise AddWorkItemError("--test-plan-phase must be non-empty (GOV-13)")
    if not request.change_reason.strip():
        raise AddWorkItemError("--change-reason must be non-empty")
    if request.test_spec_id is not None and (
        not request.test_spec_id.strip() or request.test_spec_id != request.test_spec_id.strip()
    ):
        raise AddWorkItemError("--test-spec-id must be a non-empty canonical specification id")

    work_item = db.get_work_item(request.work_item_id)
    if work_item is None:
        raise AddWorkItemError(f"work item {request.work_item_id} not found")
    phase = db.get_test_plan_phase(request.phase_id)
    if phase is None:
        raise AddWorkItemError(f"test-plan phase {request.phase_id} not found")
    phase_test_ids = _coerce_test_ids(phase.get("test_ids"))

    test_spec_id = request.test_spec_id or work_item.get("source_spec_id")
    if not isinstance(test_spec_id, str) or not test_spec_id.strip():
        raise AddWorkItemError(f"work item {request.work_item_id} has no usable source_spec_id; pass --test-spec-id")
    if db.get_spec(test_spec_id) is None:
        raise AddWorkItemError(f"test spec {test_spec_id!r} does not resolve")

    provenance = _linked_test_provenance(request.work_item_id)
    provenance_rows = (
        db._get_conn()
        .execute("SELECT * FROM current_tests WHERE description = ? ORDER BY id", (provenance,))
        .fetchall()
    )
    current_link = work_item.get("source_test_id")
    if current_link not in (None, ""):
        if not isinstance(current_link, str) or _CANONICAL_TEST_ID.fullmatch(current_link) is None:
            raise AddWorkItemError(f"work item {request.work_item_id} has noncanonical source_test_id {current_link!r}")
        linked_test = db.get_test(current_link)
        if linked_test is None:
            raise AddWorkItemError(f"work item {request.work_item_id} is linked to missing test {current_link}")
        exact_fields = {
            "title": request.test_title,
            "test_type": request.test_type,
            "expected_outcome": request.test_expected_outcome,
            "spec_id": test_spec_id,
            "description": provenance,
        }
        mismatches = [field for field, expected in exact_fields.items() if linked_test.get(field) != expected]
        if mismatches:
            raise AddWorkItemError(
                f"work item {request.work_item_id} is already linked to conflicting test "
                f"{current_link}: {', '.join(mismatches)}"
            )
        provenance_ids = [str(row["id"]) for row in provenance_rows]
        if provenance_ids != [current_link]:
            raise AddWorkItemError(f"duplicate or ambiguous add-linked-test provenance for {request.work_item_id}")
        containing_phases = _phase_ids_containing_test(db, current_link)
        if containing_phases != [request.phase_id] or current_link not in phase_test_ids:
            raise AddWorkItemError(
                f"linked test {current_link} does not belong exclusively to phase {request.phase_id}"
            )
        return {
            "already_linked": True,
            "work_item": work_item,
            "phase": phase,
            "phase_test_ids": phase_test_ids,
            "test_id": current_link,
            "test_spec_id": test_spec_id,
            "provenance": provenance,
        }

    if provenance_rows:
        raise AddWorkItemError(
            f"partial or duplicate add-linked-test provenance already exists for {request.work_item_id}"
        )
    test_id = _allocate_next_test_id(db)
    if db.get_test(test_id) is not None:
        raise AddWorkItemError(f"allocated test id {test_id} already exists; retry")
    return {
        "already_linked": False,
        "work_item": work_item,
        "phase": phase,
        "phase_test_ids": phase_test_ids,
        "test_id": test_id,
        "test_spec_id": test_spec_id,
        "provenance": provenance,
    }


def add_linked_test(
    config: GTConfig,
    request: ExistingWorkItemLinkedTestRequest,
) -> dict[str, Any]:
    """Create a test, phase membership, and existing-WI link atomically."""
    changed_by = _resolve_changed_by(Path(config.project_root))
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    try:
        if request.dry_run:
            plan = _preflight_add_linked_test(db, request)
            return {
                "created": False,
                "dry_run": True,
                "already_linked": plan["already_linked"],
                "work_item_id": request.work_item_id,
                "test_id": plan["test_id"],
                "phase_id": request.phase_id,
                "test_spec_id": plan["test_spec_id"],
            }

        conn = db._get_conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            plan = _preflight_add_linked_test(db, request)
            if plan["already_linked"]:
                conn.rollback()
                return {
                    "created": False,
                    "dry_run": False,
                    "already_linked": True,
                    "work_item_id": request.work_item_id,
                    "test_id": plan["test_id"],
                    "phase_id": request.phase_id,
                    "test_spec_id": plan["test_spec_id"],
                }

            test_id = plan["test_id"]
            test_row = db.insert_test(
                id=test_id,
                title=request.test_title,
                spec_id=plan["test_spec_id"],
                test_type=request.test_type,
                expected_outcome=request.test_expected_outcome,
                changed_by=changed_by,
                change_reason=f"GOV-12: add linked test for {request.work_item_id} ({request.change_reason})",
                description=plan["provenance"],
                commit=False,
            )
            if test_row is None:
                raise AddWorkItemError(f"insert_test for {test_id} returned None on readback")

            phase = plan["phase"]
            phase_row = db.insert_test_plan_phase(
                id=phase["id"],
                plan_id=phase["plan_id"],
                phase_order=phase["phase_order"],
                title=phase["title"],
                gate_criteria=phase["gate_criteria"],
                changed_by=changed_by,
                change_reason=f"GOV-13: assign {test_id} to phase {phase['id']} ({request.change_reason})",
                description=phase.get("description"),
                test_ids=[*plan["phase_test_ids"], test_id],
                last_result=phase.get("last_result"),
                last_executed_at=phase.get("last_executed_at"),
                commit=False,
            )
            if phase_row is None or test_id not in _coerce_test_ids(phase_row.get("test_ids")):
                raise AddWorkItemError(f"test-plan phase {request.phase_id} readback failed")

            work_item_row = db.update_work_item(
                request.work_item_id,
                changed_by=changed_by,
                change_reason=request.change_reason,
                source_test_id=test_id,
                commit=False,
            )
            if work_item_row is None or work_item_row.get("source_test_id") != test_id:
                raise AddWorkItemError(f"work item {request.work_item_id} linkage readback failed")

            final = _preflight_add_linked_test(db, request)
            if not final["already_linked"] or final["test_id"] != test_id:
                raise AddWorkItemError("atomic linked-test readback did not match the requested relationship")
            _commit_transaction(conn)
        except Exception:
            conn.rollback()
            raise

        return {
            "created": True,
            "dry_run": False,
            "already_linked": False,
            "work_item_id": request.work_item_id,
            "test_id": test_id,
            "phase_id": request.phase_id,
            "test_spec_id": plan["test_spec_id"],
        }
    except AddWorkItemError:
        raise
    except Exception as exc:
        raise AddWorkItemError(f"atomic add-linked-test transaction rolled back: {exc}") from exc
    finally:
        db.close()


def _preflight_repair(
    db: KnowledgeDB,
    request: RepairWorkItemTestLinkRequest,
) -> dict[str, Any]:
    """Prove one exact historical pair and compute its append-only repair."""
    if _CANONICAL_WORK_ITEM_ID.fullmatch(request.work_item_id) is None:
        raise AddWorkItemError(f"noncanonical work item id {request.work_item_id!r}")
    if _CANONICAL_TEST_ID.fullmatch(request.test_id) is None:
        raise AddWorkItemError(f"noncanonical test id {request.test_id!r}")
    if not request.phase_id.strip():
        raise AddWorkItemError("--test-plan-phase must be non-empty")
    if not request.change_reason.strip():
        raise AddWorkItemError("--change-reason must be non-empty")

    work_item = db.get_work_item(request.work_item_id)
    test = db.get_test(request.test_id)
    phase = db.get_test_plan_phase(request.phase_id)
    if work_item is None:
        raise AddWorkItemError(f"work item {request.work_item_id} not found")
    if test is None:
        raise AddWorkItemError(f"test {request.test_id} not found")
    if phase is None:
        raise AddWorkItemError(f"test-plan phase {request.phase_id} not found")

    expected_provenance = f"Auto-created with {request.work_item_id} via gt backlog add-work-item."
    if test.get("description") != expected_provenance:
        raise AddWorkItemError(
            f"test {request.test_id} lacks exact add-work-item provenance for {request.work_item_id}"
        )
    if not work_item.get("source_spec_id") or test.get("spec_id") != work_item.get("source_spec_id"):
        raise AddWorkItemError(f"test {request.test_id} specification does not match work item {request.work_item_id}")

    current_link = work_item.get("source_test_id")
    if current_link not in (None, "", request.test_id):
        raise AddWorkItemError(f"work item {request.work_item_id} is already linked to conflicting test {current_link}")
    claimed_by = (
        db._get_conn()
        .execute(
            "SELECT id FROM current_work_items WHERE source_test_id = ? AND id <> ? ORDER BY id",
            (request.test_id, request.work_item_id),
        )
        .fetchall()
    )
    if claimed_by:
        raise AddWorkItemError(
            f"test {request.test_id} is already linked to another work item: "
            + ", ".join(str(row["id"]) for row in claimed_by)
        )

    phase_test_ids = _coerce_test_ids(phase.get("test_ids"))
    matching_phases: list[str] = []
    rows = (
        db._get_conn()
        .execute(
            "SELECT id, test_ids FROM current_test_plan_phases WHERE test_ids LIKE ? ORDER BY id",
            (f"%{request.test_id}%",),
        )
        .fetchall()
    )
    for row in rows:
        if request.test_id in _coerce_test_ids(row["test_ids"]):
            matching_phases.append(str(row["id"]))
    unexpected_phases = [phase_id for phase_id in matching_phases if phase_id != request.phase_id]
    if unexpected_phases:
        raise AddWorkItemError(
            f"test {request.test_id} already belongs to a different phase: {', '.join(unexpected_phases)}"
        )

    update_work_item = current_link != request.test_id
    update_phase = request.test_id not in phase_test_ids
    return {
        "work_item": work_item,
        "test": test,
        "phase": phase,
        "phase_test_ids": phase_test_ids,
        "update_work_item": update_work_item,
        "update_phase": update_phase,
        "work_item_version": int(work_item["version"]) + (1 if update_work_item else 0),
        "phase_version": int(phase["version"]) + (1 if update_phase else 0),
    }


def repair_work_item_test_link(
    config: GTConfig,
    request: RepairWorkItemTestLinkRequest,
) -> dict[str, Any]:
    """Repair one exact historical work-item/test/phase relationship atomically."""
    changed_by = _resolve_changed_by(Path(config.project_root))
    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    try:
        if request.dry_run:
            plan = _preflight_repair(db, request)
            return {
                "changed": False,
                "dry_run": True,
                "already_repaired": not plan["update_work_item"] and not plan["update_phase"],
                "work_item_id": request.work_item_id,
                "test_id": request.test_id,
                "phase_id": request.phase_id,
                "work_item_version": plan["work_item_version"],
                "phase_version": plan["phase_version"],
            }

        conn = db._get_conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            plan = _preflight_repair(db, request)
            if plan["update_work_item"]:
                row = db.update_work_item(
                    request.work_item_id,
                    changed_by=changed_by,
                    change_reason=request.change_reason,
                    source_test_id=request.test_id,
                    commit=False,
                )
                if row is None or row.get("source_test_id") != request.test_id:
                    raise AddWorkItemError(f"work item {request.work_item_id} repair readback failed")
            if plan["update_phase"]:
                phase = plan["phase"]
                row = db.insert_test_plan_phase(
                    id=phase["id"],
                    plan_id=phase["plan_id"],
                    phase_order=phase["phase_order"],
                    title=phase["title"],
                    gate_criteria=phase["gate_criteria"],
                    changed_by=changed_by,
                    change_reason=request.change_reason,
                    description=phase.get("description"),
                    test_ids=[*plan["phase_test_ids"], request.test_id],
                    last_result=phase.get("last_result"),
                    last_executed_at=phase.get("last_executed_at"),
                    commit=False,
                )
                if row is None or request.test_id not in _coerce_test_ids(row.get("test_ids")):
                    raise AddWorkItemError(f"test-plan phase {request.phase_id} repair readback failed")

            final = _preflight_repair(db, request)
            if final["update_work_item"] or final["update_phase"]:
                raise AddWorkItemError("exact repair did not reach the requested relationship")
            changed = bool(plan["update_work_item"] or plan["update_phase"])
            _commit_transaction(conn)
        except Exception:
            conn.rollback()
            raise

        return {
            "changed": changed,
            "dry_run": False,
            "already_repaired": not changed,
            "work_item_id": request.work_item_id,
            "test_id": request.test_id,
            "phase_id": request.phase_id,
            "work_item_version": final["work_item_version"],
            "phase_version": final["phase_version"],
        }
    except AddWorkItemError:
        raise
    except Exception as exc:
        raise AddWorkItemError(f"exact work-item/test repair transaction rolled back: {exc}") from exc
    finally:
        db.close()
