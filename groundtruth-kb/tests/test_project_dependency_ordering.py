"""Specification-derived tests for governed project dependency ordering."""

from __future__ import annotations

from typing import Any

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleError, ProjectLifecycleService


def _create_project(
    service: ProjectLifecycleService,
    project_id: str,
    *,
    status: str = "active",
) -> dict[str, Any]:
    return service.create_project(
        project_id.removeprefix("PROJECT-").replace("-", " ").title(),
        project_id=project_id,
        status=status,
        changed_by="test",
        change_reason=f"create {project_id}",
    )


def _history_count(db: KnowledgeDB, table: str) -> int:
    return int(db._get_conn().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _add_dependency(
    service: ProjectLifecycleService,
    dependent: str,
    prerequisite: str,
    *,
    required_state: str = "active",
    affected_gate: str = "readiness",
) -> dict[str, Any]:
    return service.add_project_dependency(
        dependent,
        prerequisite,
        dependency_kind="requires_project_state",
        required_prerequisite_state=required_state,
        affected_gate=affected_gate,
        rationale=f"{dependent} requires {prerequisite}.",
        provenance="TEST-11325",
        changed_by="test",
        change_reason="add governed dependency",
    )


def test_dependency_records_are_directional_and_explain_readiness(db: KnowledgeDB) -> None:
    service = ProjectLifecycleService(db)
    _create_project(service, "PROJECT-FOUNDATION")
    _create_project(service, "PROJECT-DOWNSTREAM")

    dependency = _add_dependency(
        service,
        "PROJECT-DOWNSTREAM",
        "PROJECT-FOUNDATION",
        required_state="retired",
        affected_gate="authorization",
    )

    assert dependency["dependent_project_id"] == "PROJECT-DOWNSTREAM"
    assert dependency["prerequisite_project_id"] == "PROJECT-FOUNDATION"
    assert dependency["dependency_kind"] == "requires_project_state"
    assert dependency["required_prerequisite_state"] == "retired"
    assert dependency["affected_gate"] == "authorization"
    assert dependency["registry_version"] == 1
    assert dependency["readiness"]["satisfied"] is False
    assert dependency["readiness"]["blocked_gate"] == "authorization"
    assert dependency["readiness"]["grants_implementation_authority"] is False
    assert "recovery_route" in dependency["readiness"]
    assert "from_project_id" not in dependency
    assert "to_project_id" not in dependency

    service.update_project(
        "PROJECT-FOUNDATION",
        status="retired",
        changed_by="test",
        change_reason="complete the prerequisite",
    )

    satisfied = service.show_project_dependency(dependency["id"])
    assert satisfied["readiness"]["current_prerequisite_state"] == "retired"
    assert satisfied["readiness"]["satisfied"] is True
    assert satisfied["readiness"]["blocked_gate"] is None
    assert service.validate_project_dependencies()["valid"] is True


@pytest.mark.parametrize(
    ("required_state", "project_state"),
    (
        ("active", "active"),
        ("completed", "completed"),
        ("retired", "retired"),
        ("cancelled", "cancelled"),
    ),
)
def test_dependency_readiness_supports_each_governed_project_state(
    db: KnowledgeDB,
    required_state: str,
    project_state: str,
) -> None:
    service = ProjectLifecycleService(db)
    prerequisite_id = f"PROJECT-PREREQUISITE-{required_state.upper()}"
    dependent_id = f"PROJECT-DEPENDENT-{required_state.upper()}"
    _create_project(service, prerequisite_id)
    _create_project(service, dependent_id)
    dependency = _add_dependency(
        service,
        dependent_id,
        prerequisite_id,
        required_state=required_state,
        affected_gate="promotion",
    )

    if project_state != "active":
        service.update_project(
            prerequisite_id,
            status=project_state,
            changed_by="test",
            change_reason=f"reach {project_state}",
        )

    readiness = service.show_project_dependency(dependency["id"])["readiness"]
    assert readiness["current_prerequisite_state"] == project_state
    assert readiness["required_prerequisite_state"] == required_state
    assert readiness["satisfied"] is True
    assert readiness["blocked_gate"] is None


def test_authorization_gate_readiness_still_reports_unsatisfied_dependencies(db: KnowledgeDB) -> None:
    """The dependency gate keyed 'authorization' still computes readiness.

    WI-7657: this test previously drove ``ProjectLifecycleService.authorize_project``
    and asserted it raised while the gate was blocked, then succeeded once the
    prerequisite retired. That operation is gone -- authorization is a field on
    the project row, not an operation with its own dependency gate -- so the
    surviving behaviour is the readiness computation itself, which is what the
    dependency ordering feature actually provides.

    Non-vacuity: the absence assertion is paired with a control method that is
    still present, so a mistyped name cannot make this pass silently.
    """
    service = ProjectLifecycleService(db)
    _create_project(service, "PROJECT-FOUNDATION")
    _create_project(service, "PROJECT-DOWNSTREAM")
    service.add_project_dependency(
        "PROJECT-DOWNSTREAM",
        "PROJECT-FOUNDATION",
        required_prerequisite_state="retired",
        affected_gate="authorization",
        rationale="downstream authorization waits on foundation retirement",
        provenance="WI-7657",
        change_reason="seed authorization gate dependency",
    )

    gate = service.project_dependency_gate_readiness("PROJECT-DOWNSTREAM", "authorization")
    assert gate["ready"] is False
    assert gate["dependency_count"] == 1

    service.update_project(
        "PROJECT-FOUNDATION",
        status="retired",
        changed_by="test",
        change_reason="satisfy authorization prerequisite",
    )
    cleared = service.project_dependency_gate_readiness("PROJECT-DOWNSTREAM", "authorization")
    assert cleared["ready"] is True

    assert hasattr(service, "update_project"), "control method missing"
    assert not hasattr(service, "authorize_project")


def test_invalid_dependency_requests_append_no_versions(db: KnowledgeDB) -> None:
    service = ProjectLifecycleService(db)
    for project_id in ("PROJECT-A", "PROJECT-B", "PROJECT-C"):
        _create_project(service, project_id)
    _create_project(service, "PROJECT-RETIRED", status="retired")

    invalid_requests = (
        lambda: _add_dependency(service, "PROJECT-A", "PROJECT-A"),
        lambda: _add_dependency(service, "PROJECT-A", "PROJECT-MISSING"),
        lambda: _add_dependency(service, "PROJECT-A", "PROJECT-RETIRED"),
        lambda: service.add_project_dependency(
            "PROJECT-A",
            "PROJECT-B",
            dependency_kind="unknown-kind",
            required_prerequisite_state="active",
            affected_gate="readiness",
            rationale="invalid kind",
            provenance="TEST-11325",
            change_reason="reject invalid kind",
        ),
        lambda: service.add_project_dependency(
            "PROJECT-A",
            "PROJECT-B",
            dependency_kind="requires_project_state",
            required_prerequisite_state="unknown-state",
            affected_gate="readiness",
            rationale="invalid state",
            provenance="TEST-11325",
            change_reason="reject invalid state",
        ),
        lambda: service.add_project_dependency(
            "PROJECT-A",
            "PROJECT-B",
            dependency_kind="requires_project_state",
            required_prerequisite_state="active",
            affected_gate="unknown-gate",
            rationale="invalid gate",
            provenance="TEST-11325",
            change_reason="reject invalid gate",
        ),
    )

    for request in invalid_requests:
        before = _history_count(db, "project_dependencies")
        with pytest.raises(ProjectLifecycleError):
            request()
        assert _history_count(db, "project_dependencies") == before

    first = _add_dependency(service, "PROJECT-A", "PROJECT-B")
    before_duplicate = _history_count(db, "project_dependencies")
    with pytest.raises(ProjectLifecycleError, match="duplicate-active-edge"):
        _add_dependency(service, "PROJECT-A", "PROJECT-B")
    assert _history_count(db, "project_dependencies") == before_duplicate

    _add_dependency(service, "PROJECT-B", "PROJECT-C")
    before_cycle = _history_count(db, "project_dependencies")
    with pytest.raises(ProjectLifecycleError, match="cycle"):
        _add_dependency(service, "PROJECT-C", "PROJECT-A")
    assert _history_count(db, "project_dependencies") == before_cycle
    assert service.show_project_dependency(first["id"])["status"] == "active"


def test_dependency_retire_and_recover_are_append_only_and_revalidated(db: KnowledgeDB) -> None:
    service = ProjectLifecycleService(db)
    _create_project(service, "PROJECT-A")
    _create_project(service, "PROJECT-B")
    dependency = _add_dependency(service, "PROJECT-A", "PROJECT-B")

    retired = service.retire_project_dependency(
        dependency["id"],
        changed_by="test",
        change_reason="retire dependency",
    )
    assert retired["status"] == "retired"
    assert retired["version"] == 2

    service.update_project(
        "PROJECT-B",
        status="retired",
        changed_by="test",
        change_reason="retire endpoint while edge is inactive",
    )
    before_failed_recovery = _history_count(db, "project_dependencies")
    with pytest.raises(ProjectLifecycleError, match="retired-endpoint"):
        service.recover_project_dependency(
            dependency["id"],
            changed_by="test",
            change_reason="invalid recovery",
        )
    assert _history_count(db, "project_dependencies") == before_failed_recovery

    service.update_project(
        "PROJECT-B",
        status="active",
        changed_by="test",
        change_reason="restore endpoint",
    )
    recovered = service.recover_project_dependency(
        dependency["id"],
        changed_by="test",
        change_reason="recover dependency",
    )
    assert recovered["status"] == "active"
    assert recovered["version"] == 3
    before_invalid_transition = _history_count(db, "project_dependencies")
    with pytest.raises(ProjectLifecycleError, match="invalid-transition"):
        service.recover_project_dependency(
            dependency["id"],
            changed_by="test",
            change_reason="cannot recover an active dependency",
        )
    assert _history_count(db, "project_dependencies") == before_invalid_transition

    history = (
        db._get_conn()
        .execute(
            "SELECT version, status FROM project_dependencies WHERE id = ? ORDER BY version",
            (dependency["id"],),
        )
        .fetchall()
    )
    assert [tuple(row) for row in history] == [(1, "active"), (2, "retired"), (3, "active")]


def test_dependency_add_rolls_back_inserted_version_on_mid_transaction_failure(
    db: KnowledgeDB,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ProjectLifecycleService(db)
    _create_project(service, "PROJECT-A")
    _create_project(service, "PROJECT-B")
    original = db.add_project_dependency

    def insert_then_fail(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
        original(*args, **kwargs)
        raise RuntimeError("injected dependency write failure")

    monkeypatch.setattr(db, "add_project_dependency", insert_then_fail)
    before = {
        table: _history_count(db, table)
        for table in ("projects", "project_dependencies", "project_work_item_memberships", "work_items")
    }
    with pytest.raises(RuntimeError, match="injected dependency write failure"):
        _add_dependency(service, "PROJECT-A", "PROJECT-B")
    after = {
        table: _history_count(db, table)
        for table in ("projects", "project_dependencies", "project_work_item_memberships", "work_items")
    }
    assert after == before


def test_project_terminal_transition_cannot_invalidate_active_dependency(db: KnowledgeDB) -> None:
    service = ProjectLifecycleService(db)
    _create_project(service, "PROJECT-A")
    _create_project(service, "PROJECT-B")
    _add_dependency(service, "PROJECT-A", "PROJECT-B", required_state="active")

    before = _history_count(db, "projects")
    with pytest.raises(ProjectLifecycleError, match="would become invalid"):
        service.update_project(
            "PROJECT-B",
            status="retired",
            changed_by="test",
            change_reason="invalid endpoint transition",
        )
    assert _history_count(db, "projects") == before


def test_reorder_rolls_back_every_membership_on_mid_write_failure(
    db: KnowledgeDB,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ProjectLifecycleService(db)
    _create_project(service, "PROJECT-ORDER")
    for index, work_item_id in enumerate(("WI-ORDER-1", "WI-ORDER-2"), start=1):
        db.insert_work_item(
            id=work_item_id,
            title=work_item_id,
            origin="new",
            component="platform",
            resolution_status="open",
            stage="backlogged",
            implementation_order=90 + index,
            changed_by="test",
            change_reason="seed ordered work item",
        )
        service.add_project_item(
            "PROJECT-ORDER",
            work_item_id,
            membership_order=index,
            changed_by="test",
            change_reason="seed membership",
        )

    before_memberships = _history_count(db, "project_work_item_memberships")
    original = db.link_project_work_item
    calls = 0

    def fail_second_write(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected reorder failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(db, "link_project_work_item", fail_second_write)
    with pytest.raises(RuntimeError, match="injected"):
        service.reorder_project_items(
            "PROJECT-ORDER",
            ["WI-ORDER-2", "WI-ORDER-1"],
            start_at=5,
            changed_by="test",
            change_reason="atomic reorder",
        )

    assert _history_count(db, "project_work_item_memberships") == before_memberships
    current = db.list_project_work_items("PROJECT-ORDER")
    assert [(row["work_item_id"], row["membership_order"]) for row in current] == [
        ("WI-ORDER-1", 1),
        ("WI-ORDER-2", 2),
    ]
    assert [db.get_work_item(item_id)["implementation_order"] for item_id in ("WI-ORDER-1", "WI-ORDER-2")] == [
        91,
        92,
    ]
