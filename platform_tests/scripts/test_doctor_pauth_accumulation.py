# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5762 PAUTH accumulation doctor check fixtures.

Tests ``check_project_authorization_hygiene`` (and its ``ToolCheck`` wrapper)
with fixture ``groundtruth.db`` populated through the production
``KnowledgeDB`` API. No live MemBase read/write; no live bridge mutation.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import (
    _check_project_authorization_hygiene,
    check_project_authorization_hygiene,
)


def _seed(root: Path) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_project("Project Fixture", "test", "fixture", id="PROJECT-FIXTURE")
        db.insert_deliberation(
            "DELIB-FIXTURE",
            "owner_conversation",
            "Fixture owner decision",
            "summary",
            "content",
            "test",
            "fixture",
        )
        db.insert_spec(
            "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
            "Project implementation authorization",
            "specified",
            "test",
            "fixture",
            type="governance",
        )
    finally:
        db.close()


def _insert_authorization(
    root: Path,
    authorization_id: str,
    *,
    included: list[str] | None = None,
    forbidden: list[str] | None = None,
    allowed: list[str] | None = None,
) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_project_authorization(
            "PROJECT-FIXTURE",
            authorization_id,
            "DELIB-FIXTURE",
            "fixture scope",
            "test",
            "fixture",
            id=authorization_id,
            status="active",
            included_work_item_ids=included,
            forbidden_operations=forbidden,
            allowed_mutation_classes=allowed,
            included_spec_ids=["GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001"],
        )
    finally:
        db.close()


def _insert_work_item(
    root: Path,
    item_id: str,
    *,
    resolution_status: str = "open",
    stage: str = "created",
) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_work_item(
            item_id,
            f"Work item {item_id}",
            "hygiene",
            "backlog",
            resolution_status,
            "test",
            "seed",
            stage=stage,
            project_name="PROJECT-FIXTURE",
        )
    finally:
        db.close()


def test_multi_coverage_warns_with_covering_set(tmp_path: Path) -> None:
    """Two active authorizations sharing one included WI, identical forbidden sets -> WARN."""
    _seed(tmp_path)
    _insert_work_item(tmp_path, "WI-SHARED")
    _insert_authorization(
        tmp_path,
        "PAUTH-A",
        included=["WI-SHARED"],
        forbidden=["git_commit"],
        allowed=["source", "test"],
    )
    _insert_authorization(
        tmp_path,
        "PAUTH-B",
        included=["WI-SHARED"],
        forbidden=["git_commit"],
        allowed=["source", "test"],
    )

    payload = check_project_authorization_hygiene(tmp_path)

    assert payload["status"] == "warning"
    multi = [f for f in payload["findings"] if f["kind"] == "multi-coverage"]
    assert len(multi) == 1
    assert multi[0]["work_item_id"] == "WI-SHARED"
    assert set(multi[0]["covering_authorization_ids"]) == {"PAUTH-A", "PAUTH-B"}
    contradictory = [f for f in payload["findings"] if f["kind"] == "contradictory-authorization-set"]
    assert contradictory == []
    assert payload["summary"]["multi_coverage_count"] == 1


def test_contradictory_sets_fail(tmp_path: Path) -> None:
    """Two active authorizations on one WI with distinct forbidden sets -> FAIL."""
    _seed(tmp_path)
    _insert_work_item(tmp_path, "WI-5657")
    _insert_authorization(
        tmp_path,
        "PAUTH-FORBID",
        included=["WI-5657"],
        forbidden=["git_commit"],
        allowed=["source"],
    )
    _insert_authorization(
        tmp_path,
        "PAUTH-PERMIT",
        included=["WI-5657"],
        forbidden=[],
        allowed=["source", "test", "git_commit"],
    )

    payload = check_project_authorization_hygiene(tmp_path)
    wrapper = _check_project_authorization_hygiene(tmp_path)

    assert payload["status"] == "fail"
    contradictory = [f for f in payload["findings"] if f["kind"] == "contradictory-authorization-set"]
    assert len(contradictory) == 1
    assert contradictory[0]["work_item_id"] == "WI-5657"
    assert {c["authorization_id"] for c in contradictory[0]["covering_authorizations"]} == {
        "PAUTH-FORBID",
        "PAUTH-PERMIT",
    }
    assert wrapper.status == "fail"


def test_completion_candidate_detected(tmp_path: Path) -> None:
    """Active authorization over all-terminal WIs -> WARN; open WI authorization not flagged."""
    _seed(tmp_path)
    _insert_work_item(tmp_path, "WI-DONE-1", resolution_status="resolved", stage="resolved")
    _insert_work_item(tmp_path, "WI-DONE-2", resolution_status="verified", stage="resolved")
    _insert_work_item(tmp_path, "WI-OPEN", resolution_status="open", stage="created")
    _insert_authorization(tmp_path, "PAUTH-COMPLETE", included=["WI-DONE-1", "WI-DONE-2"])
    _insert_authorization(tmp_path, "PAUTH-ACTIVE", included=["WI-OPEN"])

    payload = check_project_authorization_hygiene(tmp_path)

    candidates = [f for f in payload["findings"] if f["kind"] == "completion-candidate"]
    assert len(candidates) == 1
    assert candidates[0]["authorization_id"] == "PAUTH-COMPLETE"
    assert set(candidates[0]["resolved_work_item_ids"]) == {"WI-DONE-1", "WI-DONE-2"}
    assert all(f["authorization_id"] != "PAUTH-ACTIVE" for f in candidates)
    assert payload["summary"]["completion_candidate_count"] == 1


def test_clean_population_passes(tmp_path: Path) -> None:
    """Single-coverage active authorizations over open WIs -> pass with summary counts."""
    _seed(tmp_path)
    _insert_work_item(tmp_path, "WI-1")
    _insert_work_item(tmp_path, "WI-2")
    _insert_authorization(tmp_path, "PAUTH-1", included=["WI-1"])
    _insert_authorization(tmp_path, "PAUTH-2", included=["WI-2"])

    payload = check_project_authorization_hygiene(tmp_path)
    wrapper = _check_project_authorization_hygiene(tmp_path)

    assert payload["status"] == "pass"
    assert payload["findings"] == []
    assert payload["summary"]["active_total"] == 2
    assert payload["summary"]["membership_wide_total"] == 0
    assert wrapper.status == "pass"


def test_missing_db_fails_closed(tmp_path: Path) -> None:
    """A fixture root without groundtruth.db -> FAIL missing-evidence."""
    payload = check_project_authorization_hygiene(tmp_path)
    wrapper = _check_project_authorization_hygiene(tmp_path)

    assert payload["status"] == "fail"
    missing = [f for f in payload["findings"] if f["kind"] == "missing-evidence"]
    assert len(missing) == 1
    assert missing[0]["severity"] == "FAIL"
    assert wrapper.status == "fail"


def test_membership_wide_authorizations_counted_informationally(tmp_path: Path) -> None:
    """Active authorizations with no explicit WI list are counted, not multi-coverage."""
    _seed(tmp_path)
    _insert_work_item(tmp_path, "WI-1")
    _insert_authorization(tmp_path, "PAUTH-MW", included=None)

    payload = check_project_authorization_hygiene(tmp_path)

    assert payload["status"] == "pass"
    assert payload["summary"]["membership_wide_total"] == 1
    assert payload["summary"]["active_total"] == 1
    assert all(f["kind"] != "multi-coverage" for f in payload["findings"])
