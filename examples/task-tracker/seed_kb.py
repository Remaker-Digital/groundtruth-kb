#!/usr/bin/env python3
"""Seed the Task Tracker knowledge database with example artifacts.

Creates: 7 specs (5 domain + 2 governance), 7 tests, 1 ADR, 1 DCL,
1 work item, 1 backlog snapshot, 1 session document.

Usage:
  python seed_kb.py              # seed from scratch
  python seed_kb.py --dry-run    # show what would be created
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure groundtruth_kb is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from groundtruth_kb.db import KnowledgeDB

DB_PATH = Path(__file__).parent / "groundtruth.db"
BY = "S1"
REASON = "Initial seed for Task Tracker example project"


def seed(db: KnowledgeDB, dry_run: bool = False) -> None:
    """Populate the KB with example artifacts."""
    if dry_run:
        print("DRY RUN — no changes will be made\n")

    # ── Governance specs ──────────────────────────────────────────────
    gov_specs = [
        (
            "GOV-01",
            "Spec-first: create specs before implementation",
            "When the owner describes requirements, record or verify specifications "
            "before writing any implementation code.",
            [{"type": "glob", "pattern": "groundtruth.db", "description": "Knowledge database exists"}],
        ),
        (
            "GOV-03",
            "Test clarity: every test has unambiguous pass/fail",
            "Every test must produce an unambiguous pass or fail result. "
            "Subjective or vague test outcomes are not acceptable.",
            [],
        ),
    ]
    for sid, title, desc, assertions in gov_specs:
        if db.get_spec(sid):
            print(f"  SKIP {sid} (exists)")
            continue
        print(f"  CREATE {sid}: {title}")
        if not dry_run:
            db.insert_spec(
                sid,
                title,
                "implemented",
                BY,
                REASON,
                description=desc,
                type="governance",
                assertions=assertions or None,
            )

    # ── Domain specs ──────────────────────────────────────────────────
    domain_specs = [
        (
            "SPEC-001",
            "Users can create tasks with title and description",
            "The API must accept POST /tasks with title (required, max 200 chars) "
            "and description (optional). Returns 201 with the created task.",
            [
                {
                    "type": "grep",
                    "file": "src/task_tracker/app.py",
                    "pattern": "POST.*tasks|post.*tasks|create_task",
                    "description": "Task creation endpoint exists",
                }
            ],
        ),
        (
            "SPEC-002",
            "Tasks transition through created -> in_progress -> done",
            "Tasks start as 'created'. Valid transitions: created->in_progress, "
            "in_progress->done. Invalid transitions return 400.",
            None,
        ),
        (
            "SPEC-003",
            "Tasks can be assigned to a user",
            "PATCH /tasks/{id} with an assignee field stores the user ID on the task.",
            None,
        ),
        (
            "SPEC-004",
            "Task list returns results in creation order",
            "GET /tasks returns all tasks ordered by creation time (oldest first).",
            None,
        ),
        (
            "SPEC-005",
            "Deleted tasks return 404 on subsequent GET",
            "After DELETE /tasks/{id}, a GET to the same ID returns 404.",
            None,
        ),
    ]
    for sid, title, desc, assertions in domain_specs:
        if db.get_spec(sid):
            print(f"  SKIP {sid} (exists)")
            continue
        print(f"  CREATE {sid}: {title}")
        if not dry_run:
            db.insert_spec(sid, title, "implemented", BY, REASON, description=desc, assertions=assertions)

    # ── Architecture decision ─────────────────────────────────────────
    if not db.get_spec("ADR-001"):
        print("  CREATE ADR-001: Use in-memory dict store for task data")
        if not dry_run:
            db.insert_spec(
                "ADR-001",
                "Use in-memory dict store for task data",
                "implemented",
                BY,
                REASON,
                type="architecture_decision",
                description=(
                    "Context: For this example project, we need a data store for tasks. "
                    "Options considered: SQLite, PostgreSQL, in-memory dict. "
                    "Decision: in-memory dict. "
                    "Rationale: keeps the focus on the GroundTruth method, not on "
                    "application database setup. "
                    "Trade-off: data does not persist across restarts. "
                    "Acceptable for a learning example. "
                    "Failed approaches: none (chosen upfront). "
                    "Consequences: simpler setup, no migration complexity, "
                    "but not suitable for production use."
                ),
                assertions=[
                    {
                        "type": "grep",
                        "file": "src/task_tracker/models.py",
                        "pattern": "class TaskStore",
                        "description": "In-memory TaskStore class exists",
                    }
                ],
            )
    else:
        print("  SKIP ADR-001 (exists)")

    # ── Design constraint ─────────────────────────────────────────────
    if not db.get_spec("DCL-001"):
        print("  CREATE DCL-001: No external database dependency")
        if not dry_run:
            db.insert_spec(
                "DCL-001",
                "No external database dependency in the application",
                "implemented",
                BY,
                REASON,
                type="design_constraint",
                description=(
                    "Derived from ADR-001. The task-tracker application must not "
                    "depend on any external database library."
                ),
                assertions=[
                    {
                        "type": "grep_absent",
                        "file": "src/task_tracker/models.py",
                        "pattern": "sqlalchemy|psycopg|pymongo",
                        "description": "No external DB library imports in models",
                    }
                ],
            )
    else:
        print("  SKIP DCL-001 (exists)")

    # ── Tests ─────────────────────────────────────────────────────────
    tests = [
        (
            "TEST-001",
            "POST /tasks returns 201",
            "SPEC-001",
            "e2e",
            "POST /tasks with valid title returns 201 and task ID",
            "tests/test_api.py",
            "TestCreateTask",
            "test_create_returns_201",
        ),
        (
            "TEST-002",
            "POST /tasks with no title returns error",
            "SPEC-001",
            "e2e",
            "POST /tasks with empty body returns 422",
            "tests/test_api.py",
            "TestCreateTask",
            "test_create_without_title_returns_422",
        ),
        (
            "TEST-003",
            "Invalid status transition returns 400",
            "SPEC-002",
            "e2e",
            "Attempting created->done returns 400",
            "tests/test_api.py",
            "TestStatusTransitions",
            "test_invalid_transition_returns_400",
        ),
        (
            "TEST-004",
            "Valid transition created -> in_progress succeeds",
            "SPEC-002",
            "e2e",
            "PATCH status=in_progress on a created task returns 200",
            "tests/test_api.py",
            "TestStatusTransitions",
            "test_valid_transition_succeeds",
        ),
        (
            "TEST-005",
            "PATCH with assignee stores user ID",
            "SPEC-003",
            "e2e",
            "Updating assignee field persists the value",
            "tests/test_api.py",
            "TestAssignment",
            "test_assignee_stored",
        ),
        (
            "TEST-006",
            "GET /tasks returns tasks in creation order",
            "SPEC-004",
            "e2e",
            "Three tasks created sequentially are returned in that order",
            "tests/test_api.py",
            "TestListOrder",
            "test_list_order",
        ),
        (
            "TEST-007",
            "DELETE then GET returns 404",
            "SPEC-005",
            "e2e",
            "After deleting a task, GET returns 404",
            "tests/test_api.py",
            "TestDelete",
            "test_delete_then_get_returns_404",
        ),
        (
            "TEST-008",
            "POST /tasks with title > 200 chars returns error",
            "SPEC-001",
            "e2e",
            "Title exceeding max_length=200 returns 422 (WI-001 remediation)",
            "tests/test_api.py",
            "TestCreateTask",
            "test_create_with_overlength_title_returns_422",
        ),
    ]
    for tid, title, spec_id, ttype, outcome, tfile, tcls, tfunc in tests:
        if db.get_test(tid):
            print(f"  SKIP {tid} (exists)")
            continue
        print(f"  CREATE {tid}: {title}")
        if not dry_run:
            db.insert_test(
                tid,
                title,
                spec_id,
                ttype,
                outcome,
                BY,
                REASON,
                test_file=tfile,
                test_class=tcls,
                test_function=tfunc,
                last_result="pass",
            )

    # ── Work item (defect found during review) ────────────────────────
    if not db.get_work_item("WI-001"):
        print("  CREATE WI-001: Add input validation for task title length")
        if not dry_run:
            db.insert_work_item(
                "WI-001",
                "Add input validation for task title length",
                origin="defect",
                component="api",
                resolution_status="resolved",
                changed_by=BY,
                change_reason="Defect found during Loyal Opposition review",
                description=(
                    "During review, the reviewer noted that SPEC-001 says 'title is "
                    "required' but the original implementation accepted titles up to "
                    "10,000 characters with no upper bound. Added max_length=200 "
                    "validation to TaskCreate and TaskUpdate models."
                ),
                source_spec_id="SPEC-001",
            )
    else:
        print("  SKIP WI-001 (exists)")

    # ── Backlog snapshot ──────────────────────────────────────────────
    if not db.get_backlog_snapshot("BL-001"):
        print("  CREATE BL-001: Initial backlog")
        if not dry_run:
            db.insert_backlog_snapshot(
                "BL-001",
                "Initial backlog — review defects",
                changed_by=BY,
                change_reason="Backlog snapshot after first review cycle",
                description="WI-001: Add input validation for task title length (defect, P2)",
                work_item_ids="WI-001",
            )
    else:
        print("  SKIP BL-001 (exists)")

    # ── Session document ──────────────────────────────────────────────
    if not db.get_document("DOC-001"):
        print("  CREATE DOC-001: Session S1 record")
        if not dry_run:
            db.insert_document(
                "DOC-001",
                "Session S1 — initial implementation of task-tracker",
                category="session_record",
                status="active",
                changed_by=BY,
                change_reason="Session record",
                content=(
                    "S1 deliverables: FastAPI task-tracker with 5 endpoints, "
                    "7 specs (5 domain + 2 GOV), 7 tests, ADR-001/DCL-001, "
                    "WI-001 (resolved), BL-001. All tests pass. Assertions clean."
                ),
            )
    else:
        print("  SKIP DOC-001 (exists)")

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Task Tracker KB")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = KnowledgeDB(db_path=DB_PATH)
    seed(db, dry_run=args.dry_run)
    db.close()


if __name__ == "__main__":
    main()
