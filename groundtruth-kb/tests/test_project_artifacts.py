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
# W1 of GTKB-GOVERNANCE-CORRECTION-S358 (WI-3365): ProjectLifecycleService
# completion + retirement under GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001
# v2. Completion and retirement are automatic once every membership-linked
# work item is VERIFIED; there is no owner-confirmation gate. The gating set
# is the project's active project-to-work-item membership links, not the
# authorization envelope's included_work_item_ids.
# ---------------------------------------------------------------------------

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from groundtruth_kb.project.lifecycle import (  # noqa: E402
    ProjectLifecycleError,
    ProjectLifecycleService,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_completion_scanner():
    """Import scripts/project_verified_completion_scanner.py for direct testing."""
    scripts_dir = _REPO_ROOT / "scripts"
    if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import project_verified_completion_scanner as scanner

    return scanner


def _write_verified_bridge(project_root: Path, wi_verified: dict[str, bool]) -> None:
    """Write bridge/INDEX.md + thread files; each WI maps to VERIFIED-or-not."""
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    lines = ["# Bridge Index", ""]
    for index, (wi, verified) in enumerate(sorted(wi_verified.items())):
        slug = f"gtkb-thread-{index}"
        top = "VERIFIED" if verified else "GO"
        (bridge / f"{slug}-001.md").write_text(f"# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8")
        lines += [f"Document: {slug}", f"{top}: bridge/{slug}-001.md", ""]
    (bridge / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_completion_env(
    project_root: Path,
    *,
    wi_verified: dict[str, bool] | None = None,
    auth_status: str = "active",
    second_active_auth: bool = False,
    linked_work_items: set[str] | None = None,
    implements_link: bool = True,
) -> KnowledgeDB:
    """Seed PROJECT-X with authorization PAUTH-X over the given work items plus
    a bridge INDEX recording their VERIFIED state. Returns an open KnowledgeDB.

    GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 gates auto-completion on
    ``project_artifact_links`` rows with ``artifact_type='bridge_thread'``,
    ``relationship='implements'``, ``status='active'``. By default each seeded
    VERIFIED thread is linked to PROJECT-X via such a row so v4-conformant
    tests need not opt in; pass ``implements_link=False`` for the
    incidental-citation case the v4 gate explicitly excludes.

    Membership-link gating (``linked_work_items``) and implements-link gating
    are independent: membership defines the gating WI set; implements defines
    which threads contribute VERIFIED coverage evidence for that set.
    """
    if wi_verified is None:
        wi_verified = {"WI-8001": True}
    _write_verified_bridge(project_root, wi_verified)
    db = KnowledgeDB(db_path=project_root / "groundtruth.db")
    db.insert_deliberation(
        "DELIB-AUTH-SEED",
        "owner_conversation",
        "Owner approved authorization",
        "Owner approved PROJECT-X authorizations.",
        "{}",
        "test",
        "seed",
        outcome="owner_decision",
    )
    db.insert_project("Completion Project", "test", "seed", id="PROJECT-X", status="active")
    db.insert_spec(
        id="SPEC-SEED",
        title="Seed spec",
        status="verified",
        changed_by="test",
        change_reason="seed",
    )
    for wi in wi_verified:
        db.insert_work_item(wi, f"Work item {wi}", "new", "backlog", "open", "test", "seed")
        if linked_work_items is None or wi in linked_work_items:
            db.link_project_work_item("PROJECT-X", wi, "test", "seed")
    db.insert_project_authorization(
        "PROJECT-X",
        "Primary authorization",
        "DELIB-AUTH-SEED",
        "Bounded scope.",
        "test",
        "seed",
        id="PAUTH-X",
        status=auth_status,
        included_work_item_ids=list(wi_verified),
        included_spec_ids=["SPEC-SEED"],
    )
    if second_active_auth:
        db.insert_project_authorization(
            "PROJECT-X",
            "Secondary authorization",
            "DELIB-AUTH-SEED",
            "Second bounded scope.",
            "test",
            "seed",
            id="PAUTH-Y",
            status="active",
            included_work_item_ids=list(wi_verified),
            included_spec_ids=["SPEC-SEED"],
        )
    if implements_link:
        # v4 D4 gate: link each seeded VERIFIED thread to PROJECT-X with
        # relationship='implements'. The thread slugs match the
        # _write_verified_bridge() naming convention (sorted by WI).
        for wi, verified in wi_verified.items():
            if not verified:
                continue
            slug_index = sorted(wi_verified).index(wi)
            slug = f"gtkb-thread-{slug_index}"
            db.add_project_artifact_link(
                "PROJECT-X",
                "bridge_thread",
                slug,
                "test",
                "seed implements link",
                relationship="implements",
            )
    return db


# --- complete_project_authorization: v2 automatic completion (no owner gate) -


def test_complete_succeeds_without_owner_decision(tmp_path) -> None:
    """v2: completion takes no owner_decision_deliberation_id and no gate."""
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["authorization"]["status"] == "completed"
    finally:
        db.close()


def test_complete_recognizes_wi_auto_verified_work_item(tmp_path) -> None:
    """Spec-intake WI-AUTO ids count as VERIFIED completion evidence."""
    db = _seed_completion_env(
        tmp_path,
        wi_verified={"WI-AUTO-SPEC-INTAKE-ABC123": True, "WI-8001": True},
    )
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["authorization"]["status"] == "completed"
    finally:
        db.close()


def test_complete_rejects_non_active_authorization(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, auth_status="revoked")
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="not active"):
            service.complete_project_authorization(
                "PAUTH-X",
                project_root=tmp_path,
                change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_when_a_wi_not_verified(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, wi_verified={"WI-8001": True, "WI-8002": False})
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="not completion-ready"):
            service.complete_project_authorization(
                "PAUTH-X",
                project_root=tmp_path,
                change_reason="complete",
            )
    finally:
        db.close()


def test_complete_rejects_when_project_has_no_membership_links(tmp_path) -> None:
    """v2 gates on membership links; a project with none cannot complete."""
    db = _seed_completion_env(tmp_path, linked_work_items=set())
    try:
        service = ProjectLifecycleService(db)
        with pytest.raises(ProjectLifecycleError, match="no active membership-linked work items"):
            service.complete_project_authorization(
                "PAUTH-X",
                project_root=tmp_path,
                change_reason="complete",
            )
    finally:
        db.close()


def test_complete_gating_set_is_membership_links_not_included_ids(tmp_path) -> None:
    """The authorization lists an unverified WI in included_work_item_ids, but
    only a VERIFIED WI is membership-linked. v2 gates on the membership link,
    so completion succeeds."""
    db = _seed_completion_env(
        tmp_path,
        wi_verified={"WI-8001": True, "WI-8002": False},
        linked_work_items={"WI-8001"},
    )
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["authorization"]["status"] == "completed"
    finally:
        db.close()


def test_complete_sole_active_authorization_retires_project(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["project_retired"] is True
        assert db.get_project("PROJECT-X")["status"] == "retired"
    finally:
        db.close()


def test_complete_with_other_active_authorization_keeps_project_active(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, second_active_auth=True)
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["project_retired"] is False
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()


# --- auto_complete_ready_authorizations: idempotent automatic transition -----


def test_auto_complete_ready_authorizations_completes_and_retires(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        completed = service.auto_complete_ready_authorizations(project_root=tmp_path)
        assert [c["authorization_id"] for c in completed] == ["PAUTH-X"]
        assert completed[0]["project_retired"] is True
        assert db.get_project_authorization("PAUTH-X")["status"] == "completed"
        assert db.get_project("PROJECT-X")["status"] == "retired"
    finally:
        db.close()


def test_auto_complete_is_idempotent(tmp_path) -> None:
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        first = service.auto_complete_ready_authorizations(project_root=tmp_path)
        second = service.auto_complete_ready_authorizations(project_root=tmp_path)
        assert len(first) == 1
        assert second == []
    finally:
        db.close()


def test_auto_complete_skips_unready_authorization(tmp_path) -> None:
    db = _seed_completion_env(tmp_path, wi_verified={"WI-8001": True, "WI-8002": False})
    try:
        service = ProjectLifecycleService(db)
        completed = service.auto_complete_ready_authorizations(project_root=tmp_path)
        assert completed == []
        assert db.get_project_authorization("PAUTH-X")["status"] == "active"
    finally:
        db.close()


# --- v4 D4 implements-gate spec-derived tests (IP-5 cases 5-6) ---------------


def test_lifecycle_verified_work_items_implements_gate(tmp_path) -> None:
    """v4 D4 gate parity at the lifecycle layer (project-scoped, NO-GO -012 F1):
    ``_verified_work_items_by_project()`` excludes a VERIFIED thread that lacks
    an active ``relationship='implements'`` link for the project; the global v3
    baseline ``_all_verified_work_items()`` still includes it (used only by the
    fail-safe surface to compute the "covered under v3" set).
    """
    db = _seed_completion_env(
        tmp_path,
        wi_verified={"WI-8001": True},
        implements_link=False,  # incidental-citation case
    )
    try:
        service = ProjectLifecycleService(db)

        # Project-scoped (the decision view): incidental citation excluded.
        by_project = service._verified_work_items_by_project(tmp_path)
        assert by_project.get("PROJECT-X", set()) == set()

        # Global v3 baseline (fail-safe diagnostic only): includes the citation.
        assert service._all_verified_work_items(tmp_path) == {"WI-8001"}

        # complete_project_authorization() uses the project-scoped path → not ready.
        with pytest.raises(ProjectLifecycleError, match="not completion-ready"):
            service.complete_project_authorization(
                "PAUTH-X",
                project_root=tmp_path,
                change_reason="complete",
            )
    finally:
        db.close()


def test_auto_complete_fail_safe_emits_manual_review(tmp_path) -> None:
    """v4 clause (d) fail-safe surface: ``auto_complete_ready_authorizations()``
    invoked with ``include_fail_safe_pauses=True`` emits a manual-review
    record for an authorization that WOULD have completed under v3 (over-broad
    incidental-citation scope) but is paused under v4 (implements-linked
    only). The default invocation (no opt-in) returns the empty list,
    preserving the existing hook contract per
    ``ADR-CODEX-HOOK-PARITY-FALLBACK-001``.
    """
    db = _seed_completion_env(
        tmp_path,
        wi_verified={"WI-8001": True},
        implements_link=False,  # the transition-window fail-safe trigger
    )
    try:
        service = ProjectLifecycleService(db)

        # Default invocation: hooks see the empty list (silent pause).
        default = service.auto_complete_ready_authorizations(project_root=tmp_path)
        assert default == []
        assert db.get_project_authorization("PAUTH-X")["status"] == "active"
        assert db.get_project("PROJECT-X")["status"] == "active"

        # Opt-in invocation: fail-safe manual-review record emitted.
        with_pauses = service.auto_complete_ready_authorizations(
            project_root=tmp_path,
            include_fail_safe_pauses=True,
        )
        assert len(with_pauses) == 1
        record = with_pauses[0]
        assert record["outcome"] == "manual_review_required"
        assert record["authorization_id"] == "PAUTH-X"
        assert record["project_id"] == "PROJECT-X"
        assert record["reason"] == "no_implements_linked_thread_covers_gating_wis"
        assert record["gating_work_items"] == ["WI-8001"]
        assert record["covered_under_v3"] == ["WI-8001"]
        assert record["missing_under_v4"] == ["WI-8001"]
        # No mutation occurred: authorization still active, project still active.
        assert db.get_project_authorization("PAUTH-X")["status"] == "active"
        assert db.get_project("PROJECT-X")["status"] == "active"
    finally:
        db.close()


def test_auto_complete_does_not_cross_project_retire(tmp_path) -> None:
    """v4 F1 regression (NO-GO -012) at the lifecycle layer: an ``implements``
    link held by PROJECT-A must NOT complete or retire PROJECT-B, even when
    PROJECT-A's VERIFIED thread cites a WI that gates PROJECT-B.

    The prior global-slug implementation would have auto-completed and retired
    PROJECT-B because WI-8002 entered the global verified set. The project-scoped
    map attributes thread-a's coverage to PROJECT-A only.
    """
    bridge = tmp_path / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / "thread-a-001.md").write_text(
        "NEW\n\n# Impl report\n\nWork Item: WI-8002\n", encoding="utf-8"
    )
    (bridge / "thread-a-002.md").write_text("VERIFIED\n\n# Codex verdict\n", encoding="utf-8")
    (bridge / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: thread-a\n"
        "VERIFIED: bridge/thread-a-002.md\nNEW: bridge/thread-a-001.md\n\n",
        encoding="utf-8",
    )

    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED", "owner_conversation", "seed", "seed", "{}", "t", "s",
            outcome="owner_decision",
        )
        db.insert_spec(id="SPEC-SEED", title="Seed", status="verified", changed_by="t", change_reason="s")
        db.insert_project("Project A", "t", "s", id="PROJECT-A", status="active")
        db.insert_project("Project B", "t", "s", id="PROJECT-B", status="active")
        # WI-8002 gates PROJECT-B; only PROJECT-A implements-links thread-a.
        db.insert_work_item("WI-8002", "shared WI", "new", "backlog", "open", "t", "s")
        db.link_project_work_item("PROJECT-B", "WI-8002", "t", "s")
        db.add_project_artifact_link(
            "PROJECT-A", "bridge_thread", "thread-a", "t", "s", relationship="implements",
        )
        db.insert_project_authorization(
            "PROJECT-B", "Auth B", "DELIB-SEED", "Bounded scope.", "t", "s",
            id="PAUTH-B", status="active",
            included_work_item_ids=["WI-8002"], included_spec_ids=["SPEC-SEED"],
        )

        service = ProjectLifecycleService(db)
        # PROJECT-B verified set is empty (no implements link) → not completed.
        assert service._verified_work_items_by_project(tmp_path).get("PROJECT-B", set()) == set()
        completed = service.auto_complete_ready_authorizations(project_root=tmp_path)
        assert all(c["project_id"] != "PROJECT-B" for c in completed), (
            "F1 regression: PROJECT-A's implements link must not auto-complete PROJECT-B"
        )
        # PROJECT-B remains active and un-retired; PAUTH-B still active.
        assert db.get_project("PROJECT-B")["status"] == "active"
        assert db.get_project_authorization("PAUTH-B")["status"] == "active"
        # complete_project_authorization() also refuses PROJECT-B directly.
        with pytest.raises(ProjectLifecycleError, match="not completion-ready"):
            service.complete_project_authorization(
                "PAUTH-B", project_root=tmp_path, change_reason="complete",
            )
    finally:
        db.close()


# --- scanner gating-set parity with the lifecycle service --------------------


def test_scanner_gating_set_uses_membership_links(tmp_path) -> None:
    """The completion scanner sources its gating set from the project's
    membership links, agreeing with the lifecycle service."""
    scanner = _load_completion_scanner()
    db = _seed_completion_env(
        tmp_path,
        wi_verified={"WI-8001": True, "WI-8002": False},
        linked_work_items={"WI-8001"},
    )
    db.close()
    ready = scanner.completion_ready(tmp_path)
    assert [r.authorization_id for r in ready] == ["PAUTH-X"]
    assert ready[0].verified_work_item_ids == ["WI-8001"]


# --- gt projects complete-authorization CLI subcommand -----------------------


def test_projects_complete_authorization_cli(project_dir, runner: CliRunner) -> None:
    config_flag = ["--config", str(project_dir / "groundtruth.toml")]
    db = _seed_completion_env(project_dir)
    db.close()

    result = runner.invoke(
        main,
        [
            *config_flag,
            "projects",
            "complete-authorization",
            "PAUTH-X",
            "--change-reason",
            "W1 CLI completion test",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["authorization"]["status"] == "completed"
    assert payload["project_retired"] is True


# --- v3 collective retirement: associated work items + membership links ------


def test_complete_retires_membership_linked_work_items(tmp_path) -> None:
    """GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 collective retirement:
    completing the sole active authorization retires the project AND
    transitions its membership-linked work item to resolution_status='retired'
    AND retires the membership link."""
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["project_retired"] is True
        assert result["retired_work_items"] == ["WI-8001"]
        assert db.get_work_item("WI-8001")["resolution_status"] == "retired"
        # The membership link is retired (non-active) -> absent from the active
        # set, but preserved append-only with status 'retired'.
        assert db.list_project_work_items("PROJECT-X") == []
        all_memberships = db.list_project_work_items("PROJECT-X", include_inactive=True)
        assert [m["membership_status"] for m in all_memberships] == ["retired"]
    finally:
        db.close()


def test_complete_shared_work_item_is_not_retired(tmp_path) -> None:
    """Collective retirement, shared-work-item case: a work item that is also
    an active member of another non-terminal project is left active when one
    of its projects retires; only the retiring project's membership link is
    retired."""
    db = _seed_completion_env(tmp_path)
    try:
        db.insert_project("Other Project", "test", "seed", id="PROJECT-OTHER", status="active")
        db.link_project_work_item("PROJECT-OTHER", "WI-8001", "test", "seed")
        service = ProjectLifecycleService(db)
        result = service.complete_project_authorization(
            "PAUTH-X",
            project_root=tmp_path,
            change_reason="complete",
        )
        assert result["project_retired"] is True
        # WI-8001 is shared with the still-active PROJECT-OTHER -> not retired.
        assert result["retired_work_items"] == []
        assert db.get_work_item("WI-8001")["resolution_status"] != "retired"
        # PROJECT-X's membership link is retired; PROJECT-OTHER's stays active.
        assert db.list_project_work_items("PROJECT-X") == []
        assert [m["work_item_id"] for m in db.list_project_work_items("PROJECT-OTHER")] == ["WI-8001"]
    finally:
        db.close()


def test_auto_complete_retires_membership_linked_work_items(tmp_path) -> None:
    """auto_complete_ready_authorizations applies collective retirement and
    reports the retired work items in its result."""
    db = _seed_completion_env(tmp_path)
    try:
        service = ProjectLifecycleService(db)
        completed = service.auto_complete_ready_authorizations(project_root=tmp_path)
        assert len(completed) == 1
        assert completed[0]["retired_work_items"] == ["WI-8001"]
        assert db.get_work_item("WI-8001")["resolution_status"] == "retired"
    finally:
        db.close()
