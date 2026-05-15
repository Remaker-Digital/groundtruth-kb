"""Tests for first-class project artifacts over canonical work_items."""

from __future__ import annotations

import json

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def _insert_work_item(db: KnowledgeDB, item_id: str, **fields: object) -> dict[str, object] | None:
    defaults = {
        "title": f"Work item {item_id}",
        "origin": "new",
        "component": "backlog",
        "resolution_status": "open",
        "changed_by": "test",
        "change_reason": "create test work item",
    }
    defaults.update(fields)
    return db.insert_work_item(id=item_id, **defaults)


def test_project_schema_preserves_work_item_authority(db: KnowledgeDB) -> None:
    conn = db._get_conn()
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    views = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'view'")}

    assert {
        "projects",
        "project_work_item_memberships",
        "project_dependencies",
        "project_artifact_links",
    } <= tables
    assert {
        "current_projects",
        "current_project_work_item_memberships",
        "current_project_dependencies",
        "current_project_artifact_links",
        "current_work_items",
    } <= views
    assert "work_items" in tables
    assert "backlog_items" not in tables
    assert "backlog_entries" not in tables
    assert "subjects" not in tables


def test_work_item_can_belong_to_multiple_projects_without_duplication(db: KnowledgeDB) -> None:
    _insert_work_item(db, "WI-MULTI", title="Shared implementation")
    db.insert_project("Project Alpha", "test", "create", id="PROJECT-ALPHA", rank=1)
    db.insert_project("Project Beta", "test", "create", id="PROJECT-BETA", rank=2)

    db.link_project_work_item("PROJECT-ALPHA", "WI-MULTI", "test", "link")
    db.link_project_work_item("PROJECT-BETA", "WI-MULTI", "test", "link")

    alpha_items = db.list_project_work_items("PROJECT-ALPHA")
    beta_items = db.list_project_work_items("PROJECT-BETA")
    work_items = db.list_work_items()

    assert [item["work_item_id"] for item in alpha_items] == ["WI-MULTI"]
    assert [item["work_item_id"] for item in beta_items] == ["WI-MULTI"]
    assert [item["id"] for item in work_items] == ["WI-MULTI"]


def test_project_dependencies_are_queryable_independently(db: KnowledgeDB) -> None:
    _insert_work_item(db, "WI-8002LOCKER", title="Shared blocker")
    db.insert_project("Foundation", "test", "create", id="PROJECT-FOUNDATION")
    db.insert_project("Release", "test", "create", id="PROJECT-RELEASE")

    dependency = db.add_project_dependency(
        "PROJECT-RELEASE",
        "PROJECT-FOUNDATION",
        "test",
        "record dependency",
        rationale="Release needs foundation complete first.",
        related_work_item_id="WI-8002LOCKER",
    )

    dependencies = db.list_project_dependencies("PROJECT-RELEASE")
    assert dependency is not None
    assert dependency["from_project_id"] == "PROJECT-RELEASE"
    assert dependency["to_project_id"] == "PROJECT-FOUNDATION"
    assert dependencies[0]["related_work_item_id"] == "WI-8002LOCKER"


def test_project_artifact_links_cover_bridge_deliberation_and_spec(db: KnowledgeDB) -> None:
    db.insert_project("Evidence Project", "test", "create", id="PROJECT-EVIDENCE")

    db.add_project_artifact_link("PROJECT-EVIDENCE", "bridge", "gtkb-first-class-project-artifacts", "test", "link")
    db.add_project_artifact_link("PROJECT-EVIDENCE", "deliberation", "DELIB-0838", "test", "link")
    db.add_project_artifact_link("PROJECT-EVIDENCE", "spec", "GOV-FILE-BRIDGE-AUTHORITY-001", "test", "link")

    links = db.list_project_artifact_links("PROJECT-EVIDENCE")
    assert {(link["artifact_type"], link["artifact_ref"]) for link in links} == {
        ("bridge", "gtkb-first-class-project-artifacts"),
        ("deliberation", "DELIB-0838"),
        ("spec", "GOV-FILE-BRIDGE-AUTHORITY-001"),
    }


def test_compatibility_backfill_maps_project_strings_to_project_memberships(tmp_path) -> None:
    db_path = tmp_path / "project-backfill.db"
    db = KnowledgeDB(db_path=db_path)
    _insert_work_item(
        db,
        "WI-8002ACKFILL",
        title="Backfilled item",
        project_name="Platform Upgrade",
        subproject_name="Bridge Automation",
        implementation_order=7,
    )
    db.close()

    reopened = KnowledgeDB(db_path=db_path)
    try:
        root_project = reopened.get_project("PROJECT-PLATFORM-UPGRADE")
        subproject = reopened.get_project("PROJECT-PLATFORM-UPGRADE-BRIDGE-AUTOMATION")
        root_items = reopened.list_project_work_items("PROJECT-PLATFORM-UPGRADE")
        subproject_items = reopened.list_project_work_items("PROJECT-PLATFORM-UPGRADE-BRIDGE-AUTOMATION")
    finally:
        reopened.close()

    assert root_project is not None
    assert root_project["source_project_name"] == "Platform Upgrade"
    assert subproject is not None
    assert subproject["parent_project_id"] == "PROJECT-PLATFORM-UPGRADE"
    assert [item["work_item_id"] for item in root_items] == ["WI-8002ACKFILL"]
    assert [item["work_item_id"] for item in subproject_items] == ["WI-8002ACKFILL"]


def test_project_summary_counts_project_layer(db: KnowledgeDB) -> None:
    db.insert_project("Summary Project", "test", "create", id="PROJECT-SUMMARY")
    summary = db.get_summary()

    assert summary["project_total"] == 1
    assert summary["project_counts"] == {"active": 1}
    assert summary["project_membership_count"] == 0


def test_projects_cli_show_reports_members_from_current_work_items(project_dir, runner: CliRunner) -> None:
    config_flag = ["--config", str(project_dir / "groundtruth.toml")]
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        _insert_work_item(db, "WI-CLI", title="CLI visible item")
        db.insert_project("CLI Project", "test", "create", id="PROJECT-CLI")
        db.link_project_work_item("PROJECT-CLI", "WI-CLI", "test", "link")
    finally:
        db.close()

    result = runner.invoke(main, [*config_flag, "projects", "show", "PROJECT-CLI", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project"]["id"] == "PROJECT-CLI"
    assert payload["work_items"][0]["work_item_id"] == "WI-CLI"
    assert payload["work_items"][0]["work_item_title"] == "CLI visible item"


# ---------------------------------------------------------------------------
# IP-3 of WI-3316: ProjectLifecycleService.complete_project_authorization()
# (bridge thread gtkb-project-verified-completion-auq-trigger).
# ---------------------------------------------------------------------------

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from groundtruth_kb.project.lifecycle import (  # noqa: E402
    ProjectLifecycleError,
    ProjectLifecycleService,
)


def _write_verified_bridge(project_root: Path, wi_verified: dict[str, bool]) -> None:
    """Write bridge/INDEX.md + thread files; each WI maps to VERIFIED-or-not."""
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    lines = ["# Bridge Index", ""]
    for index, (wi, verified) in enumerate(sorted(wi_verified.items())):
        slug = f"gtkb-thread-{index}"
        top = "VERIFIED" if verified else "GO"
        (bridge / f"{slug}-001.md").write_text(
            f"# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8"
        )
        lines += [f"Document: {slug}", f"{top}: bridge/{slug}-001.md", ""]
    (bridge / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_completion_env(
    project_root: Path,
    *,
    wi_verified: dict[str, bool] | None = None,
    auth_status: str = "active",
    second_active_auth: bool = False,
) -> KnowledgeDB:
    """Seed PROJECT-X with authorization PAUTH-X over the given WIs plus a
    bridge INDEX recording their VERIFIED state. Returns an open KnowledgeDB."""
    if wi_verified is None:
        wi_verified = {"WI-8001": True}
    _write_verified_bridge(project_root, wi_verified)
    db = KnowledgeDB(db_path=project_root / "groundtruth.db")
    db.insert_deliberation(
        "DELIB-AUTH-SEED", "owner_conversation", "Owner approved authorization",
        "Owner approved PROJECT-X authorizations.", "{}", "test", "seed",
        outcome="owner_decision",
    )
    db.insert_project("Completion Project", "test", "seed", id="PROJECT-X", status="active")
    db.insert_spec(
        id="SPEC-SEED", title="Seed spec", status="verified",
        changed_by="test", change_reason="seed",
    )
    for wi in wi_verified:
        db.insert_work_item(wi, f"Work item {wi}", "new", "backlog", "open", "test", "seed")
    db.insert_project_authorization(
        "PROJECT-X", "Primary authorization", "DELIB-AUTH-SEED",
        "Bounded scope.", "test", "seed", id="PAUTH-X", status=auth_status,
        included_work_item_ids=list(wi_verified), included_spec_ids=["SPEC-SEED"],
    )
    if second_active_auth:
        db.insert_project_authorization(
            "PROJECT-X", "Secondary authorization", "DELIB-AUTH-SEED",
            "Second bounded scope.", "test", "seed", id="PAUTH-Y", status="active",
            included_work_item_ids=list(wi_verified), included_spec_ids=["SPEC-SEED"],
        )
    return db


def _insert_owner_decision(db: KnowledgeDB, delib_id: str, content: str) -> None:
    db.insert_deliberation(
        delib_id, "owner_conversation", "Owner completion decision",
        "Owner confirmed an authorization completion.", content, "test",
        "owner decision", outcome="owner_decision",
    )


def test_complete_rejects_missing_deliberation(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="not found"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-DOES-NOT-EXIST",
                project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_lo_review_deliberation(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    db.insert_deliberation(
        "DELIB-LO", "lo_review", "LO review", "An LO review of PROJECT-X.",
        "PROJECT-X reviewed by Loyal Opposition.", "test", "lo review",
        outcome="no_go",
    )
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="owner conversation"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-LO", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_informational_deliberation(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    db.insert_deliberation(
        "DELIB-INFO", "owner_conversation", "Informational note",
        "An informational note about PROJECT-X.", "PROJECT-X status note.",
        "test", "note", outcome="informational",
    )
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="owner decision"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-INFO", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_no_go_deliberation(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    db.insert_deliberation(
        "DELIB-NOGO", "owner_conversation", "No-go note",
        "Owner conversation that ended no-go for PROJECT-X.", "PROJECT-X no-go.",
        "test", "no-go", outcome="no_go",
    )
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="owner decision"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-NOGO", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_owner_decision_for_other_project(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    _insert_owner_decision(db, "DELIB-OTHER", "Owner approved completion of PROJECT-OTHER.")
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="completion context"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-OTHER", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_non_active_authorization(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, auth_status="revoked")
    _insert_owner_decision(db, "DELIB-OK", "Owner approved completion of PROJECT-X / PAUTH-X.")
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="not active"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-OK", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_when_a_wi_not_verified(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, wi_verified={"WI-8001": True, "WI-8002": False})
    _insert_owner_decision(db, "DELIB-OK", "Owner approved completion of PROJECT-X / PAUTH-X.")
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="not completion-ready"):
            service.complete_project_authorization(
                "PAUTH-X", "DELIB-OK", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


def test_complete_accepts_valid_owner_decision_deliberation(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    _insert_owner_decision(db, "DELIB-OK", "Owner approved completion of PROJECT-X / PAUTH-X.")
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X", "DELIB-OK", project_root=tmp_path, change_reason="complete",
        )
        assert result["authorization"]["status"] == "completed"
    finally:
        db.close()


def test_complete_sole_active_authorization_retires_project(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    _insert_owner_decision(db, "DELIB-OK", "Owner approved completion of PROJECT-X / PAUTH-X.")
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X", "DELIB-OK", project_root=tmp_path, change_reason="complete",
        )
        assert result["project_retired"] is True
        assert db.get_project("PROJECT-X")["status"] == "retired"
    finally:
        db.close()


def test_complete_with_other_active_authorization_keeps_project_active(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, second_active_auth=True)
    _insert_owner_decision(db, "DELIB-OK", "Owner approved completion of PROJECT-X / PAUTH-X.")
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X", "DELIB-OK", project_root=tmp_path, change_reason="complete",
        )
        assert result["project_retired"] is False
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()
