"""Tests for first-class project artifacts over canonical work_items."""

from __future__ import annotations

import sqlite3

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


def test_project_summary_counts_project_layer(db: KnowledgeDB) -> None:
    db.insert_project("Summary Project", "test", "create", id="PROJECT-SUMMARY")
    summary = db.get_summary()

    assert summary["project_total"] == 1
    assert summary["project_counts"] == {"active": 1}
    assert summary["project_membership_count"] == 0


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
        (bridge / f"{slug}-001.md").write_text(f"{top}\n\n# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8")
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


def _add_completion_guard(
    db: KnowledgeDB,
    *,
    artifact_type: str = "completion_guard",
    artifact_ref: str = "plan-incomplete-fixture",
    status: str = "active",
    link_id: str = "PAL-PLAN-INCOMPLETE",
) -> None:
    db.add_project_artifact_link(
        "PROJECT-X",
        artifact_type,
        artifact_ref,
        "test",
        "seed plan_incomplete guard",
        relationship="plan_incomplete",
        status=status,
        notes="Fixture guard",
        id=link_id,
    )


# --- complete_project_authorization: v2 automatic completion (no owner gate) -


# --- auto_complete_ready_authorizations: idempotent automatic transition -----


# --- v4 D4 implements-gate spec-derived tests (IP-5 cases 5-6) ---------------


# --- scanner gating-set parity with the lifecycle service --------------------


# --- gt projects complete-authorization CLI subcommand -----------------------


# --- v3 collective retirement: associated work items + membership links ------


# --- WI-4737 related_bridge_threads id-agnostic recognition path -------------


def _seed_noncanonical_recognition_env(project_root: Path) -> KnowledgeDB:
    """Seed PROJECT-X with a non-canonical-id WI whose VERIFIED implements-linked
    thread carries NO regex-parseable ``Work Item:`` line, but whose
    ``related_bridge_threads`` names that thread. Returns an open KnowledgeDB.
    """
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / "gtkb-noncanon-thread-001.md").write_text(
        "VERIFIED\n\n# Verified report\n\nWork Item: new work item to be created later\n",
        encoding="utf-8",
    )
    (bridge / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: gtkb-noncanon-thread\nVERIFIED: bridge/gtkb-noncanon-thread-001.md\n\n",
        encoding="utf-8",
    )
    db = KnowledgeDB(db_path=project_root / "groundtruth.db")
    db.insert_deliberation(
        "DELIB-SEED",
        "owner_conversation",
        "Owner approved",
        "Owner approved.",
        "{}",
        "test",
        "seed",
        outcome="owner_decision",
    )
    db.insert_project("Lifecycle Project", "test", "seed", id="PROJECT-X", status="active")
    db.insert_work_item(
        "WI-NONCANON-RECOG-001",
        "Work item",
        "new",
        "backlog",
        "open",
        "test",
        "seed",
        related_bridge_threads='["gtkb-noncanon-thread"]',
    )
    db.link_project_work_item("PROJECT-X", "WI-NONCANON-RECOG-001", "test", "seed")
    db.insert_spec(id="SPEC-SEED", title="Seed spec", status="verified", changed_by="test", change_reason="seed")
    db.add_project_artifact_link(
        "PROJECT-X",
        "bridge_thread",
        "gtkb-noncanon-thread",
        "test",
        "seed implements link",
        relationship="implements",
    )
    return db


# ---------------------------------------------------------------------------
# WI-5292 — concurrency-safe project artifact backfill
# ---------------------------------------------------------------------------


def _make_backfill_db(tmp_path, project: str = "Proj A", item: str = "WI-5292-FX"):
    """Return a fresh KnowledgeDB with a compatibility work item whose project
    row and membership are missing (so the backfill must append them)."""
    db_path = tmp_path / "backfill.db"
    db = KnowledgeDB(db_path=db_path)
    _insert_work_item(
        db,
        item,
        project_name=project,
        subproject_name="Sub",
        implementation_order=1,
    )
    # Close and reopen so _backfill runs during schema ensure on a fresh conn.
    db.close()
    return db_path


def _counts(db_path):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        projects = conn.execute("SELECT COUNT(*) FROM current_projects").fetchone()[0]
        memberships = conn.execute("SELECT COUNT(*) FROM current_project_work_item_memberships").fetchone()[0]
    finally:
        conn.close()
    return projects, memberships


def _wi5292_spawn_worker(args: tuple) -> None:
    """Spawn-pool worker: open a fresh KnowledgeDB on the shared db and insert
    one compatibility work item (triggering the schema/backfill path)."""
    db_path, idx = args
    db = KnowledgeDB(db_path=Path(db_path))
    try:
        _insert_work_item(db, f"WI-5292-W{idx}", project_name=f"Proj {idx}", subproject_name="Sub")
    finally:
        db.close()
