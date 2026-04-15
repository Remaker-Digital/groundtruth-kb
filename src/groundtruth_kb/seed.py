"""
GroundTruth KB — Generic seed data.

Provides starter governance specs (the GroundTruth method itself) and
optional example domain specs + tests for new projects.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB


# ---------------------------------------------------------------------------
# Governance seeds — the GroundTruth method
# ---------------------------------------------------------------------------

_GOVERNANCE_SPECS: list[dict[str, Any]] = [
    {
        "id": "GOV-01",
        "title": "Specification First",
        "description": (
            "Before implementing any feature or change, create or update "
            "the relevant specification in the knowledge database. "
            "Code follows specs, not the reverse."
        ),
        "type": "governance",
        "priority": "P0",
        "status": "verified",
        "assertions": [
            {
                "type": "glob",
                "pattern": "**/groundtruth.toml",
                "description": "Project has a groundtruth.toml config file",
            },
        ],
    },
    {
        "id": "GOV-02",
        "title": "Owner Consent",
        "description": (
            "Specifications are immutable without owner approval. "
            "Changes to agreed specs require explicit owner consent "
            "before implementation proceeds."
        ),
        "type": "governance",
        "priority": "P0",
        "status": "verified",
    },
    {
        "id": "GOV-03",
        "title": "Test Clarity",
        "description": (
            "Every test must produce an unambiguous PASS or FAIL result. "
            "Tests that require subjective interpretation are invalid."
        ),
        "type": "governance",
        "priority": "P0",
        "status": "verified",
    },
    {
        "id": "GOV-05",
        "title": "Fix Specification First",
        "description": (
            "When a test fails, first verify the specification is correct, "
            "then verify the test is correct, then fix the implementation. "
            "Never change a test to match broken behavior."
        ),
        "type": "governance",
        "priority": "P0",
        "status": "verified",
    },
    {
        "id": "GOV-08",
        "title": "Knowledge Database Is Truth",
        "description": (
            "All project knowledge — specifications, tests, work items, "
            "decisions, and procedures — lives in the knowledge database. "
            "External documents reference the KB, not the reverse."
        ),
        "type": "governance",
        "priority": "P0",
        "status": "verified",
    },
]


# ---------------------------------------------------------------------------
# Example domain seeds — a simple "task tracker" project
# ---------------------------------------------------------------------------

_EXAMPLE_SPECS: list[dict[str, Any]] = [
    {
        "id": "SPEC-001",
        "title": "Task creation",
        "description": (
            "Users can create tasks with a title (required, max 200 chars), "
            "description (optional), and priority (low/medium/high, default medium). "
            "Created tasks have status 'open' and a UTC timestamp."
        ),
        "type": "requirement",
        "priority": "P1",
        "status": "specified",
        "assertions": [
            {
                "type": "grep",
                "pattern": "def create_task",
                "file": "src/tasks.py",
                "description": "create_task function exists",
            },
            {
                "type": "grep",
                "pattern": "status.*=.*['\"]open['\"]",
                "file": "src/tasks.py",
                "min_count": 1,
                "description": "Default status is 'open'",
            },
        ],
    },
    {
        "id": "SPEC-002",
        "title": "Task listing with filters",
        "description": (
            "Users can list tasks filtered by status (open/in_progress/done) "
            "and/or priority. Results are ordered by creation date (newest first). "
            "Returns an empty list when no tasks match."
        ),
        "type": "requirement",
        "priority": "P1",
        "status": "specified",
        "assertions": [
            {
                "type": "grep",
                "pattern": "def list_tasks",
                "file": "src/tasks.py",
                "description": "list_tasks function exists",
            },
        ],
    },
    {
        "id": "SPEC-003",
        "title": "Task completion",
        "description": (
            "Users can mark a task as 'done'. Completing a task records "
            "a completion timestamp. Completed tasks cannot be re-opened "
            "(create a new task instead)."
        ),
        "type": "requirement",
        "priority": "P2",
        "status": "specified",
    },
]

_EXAMPLE_TESTS: list[dict[str, Any]] = [
    {
        "id": "TEST-001",
        "spec_id": "SPEC-001",
        "title": "Create task with valid title",
        "description": (
            "Given a title 'Fix login bug', when create_task is called, "
            "then a task is returned with status 'open' and the given title."
        ),
        "expected_outcome": "Task returned with status='open', title matches input, created_at is set.",
        "test_type": "unit",
    },
    {
        "id": "TEST-002",
        "spec_id": "SPEC-001",
        "title": "Create task rejects empty title",
        "description": "Given an empty string title, when create_task is called, then a ValueError is raised.",
        "expected_outcome": "ValueError raised with message about empty title.",
        "test_type": "unit",
    },
    {
        "id": "TEST-003",
        "spec_id": "SPEC-002",
        "title": "List tasks returns all when no filter",
        "description": (
            "Given 3 tasks exist, when list_tasks is called with no filters, "
            "then all 3 tasks are returned newest first."
        ),
        "expected_outcome": "Returns list of 3 tasks ordered by created_at DESC.",
        "test_type": "unit",
    },
    {
        "id": "TEST-004",
        "spec_id": "SPEC-002",
        "title": "List tasks filters by status",
        "description": (
            "Given tasks with mixed statuses, when list_tasks(status='open') is called, "
            "then only open tasks are returned."
        ),
        "expected_outcome": "Returns only tasks where status='open'.",
        "test_type": "unit",
    },
    {
        "id": "TEST-005",
        "spec_id": "SPEC-003",
        "title": "Complete task records timestamp",
        "description": (
            "Given an open task, when complete_task is called, then the task status is 'done' and completed_at is set."
        ),
        "expected_outcome": "Task status changed to 'done', completed_at timestamp is set.",
        "test_type": "unit",
    },
]


def load_governance_seeds(db: KnowledgeDB) -> int:
    """Insert governance specs if they don't already exist. Returns count inserted."""
    count = 0
    for spec_data in _GOVERNANCE_SPECS:
        existing = db.get_spec(spec_data["id"])
        if existing:
            continue
        db.insert_spec(
            id=spec_data["id"],
            title=spec_data["title"],
            description=spec_data["description"],
            status=spec_data["status"],
            priority=spec_data.get("priority", "P0"),
            changed_by="gt-seed",
            change_reason="Initial governance seed",
            type=spec_data.get("type", "governance"),
            assertions=spec_data.get("assertions"),
        )
        count += 1
    return count


def load_example_seeds(db: KnowledgeDB) -> int:
    """Insert example domain specs and tests. Returns total count inserted."""
    count = 0

    for spec_data in _EXAMPLE_SPECS:
        existing = db.get_spec(spec_data["id"])
        if existing:
            continue
        db.insert_spec(
            id=spec_data["id"],
            title=spec_data["title"],
            description=spec_data["description"],
            status=spec_data["status"],
            priority=spec_data.get("priority", "P1"),
            changed_by="gt-seed",
            change_reason="Example domain seed",
            type=spec_data.get("type", "requirement"),
            assertions=spec_data.get("assertions"),
        )
        count += 1

    for test_data in _EXAMPLE_TESTS:
        existing = db.get_test(test_data["id"])
        if existing:
            continue
        db.insert_test(
            id=test_data["id"],
            spec_id=test_data["spec_id"],
            title=test_data["title"],
            test_type=test_data.get("test_type", "unit"),
            expected_outcome=test_data["expected_outcome"],
            changed_by="gt-seed",
            change_reason="Example test seed",
            description=test_data.get("description"),
        )
        count += 1

    return count
