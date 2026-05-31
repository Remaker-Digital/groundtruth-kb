"""Tests for the governed ``gt projects reconcile-doubled-prefix`` CLI service.

Authority: bridge/gtkb-phantom-project-prefix-reconciliation-003.md
(REVISED-1), Codex GO at bridge/gtkb-phantom-project-prefix-reconciliation-004.md.
Source work item: WI-3355.

Covers the 10-test Specification-Derived Verification Plan:

* T1 ``--dry-run`` (default) lists every phantom with the correct
  ``canonical_id`` and per-phantom membership counts.
* T2 ``--dry-run`` makes no DB writes (sha256 of the db file is
  byte-identical before/after).
* T3 ``--apply`` re-links a WI whose canonical project is active and
  lacks the equivalent membership.
* T4 ``--apply`` re-links a WI whose canonical project is RETIRED and
  lacks the equivalent membership (the DELIB-2506 disposition path).
* T5 ``--apply`` does NOT create a duplicate canonical membership when
  one already exists for the same WI (the redundant case; covers the 42
  of 49 inventory rows that take this branch).
* T6 ``--apply`` supersedes each phantom membership row (new version
  inserted with ``status='superseded'``; same membership id).
* T7 ``--apply`` retires each phantom project (new version inserted with
  ``status='retired'``).
* T8 ``--apply`` is idempotent on rerun (second pass makes zero writes).
* T9 ``--apply --json`` emits a structured per-phantom report with
  reconciliation counts (shape-locked).
* T10 a phantom with MISSING canonical is skipped and reported (the
  safety branch).

Every test runs against a temporary ``groundtruth.db`` created from a temp
``groundtruth.toml``; no test mutates the canonical ``groundtruth.db``,
``memory/MEMORY.md``, or ``memory/work_list.md``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.cli_projects_reconcile import (  # noqa: E402
    PHANTOM_PREFIX,
    ReconcileRequest,
    _canonical_id_from_phantom,
    build_reconcile_plan,
)
from groundtruth_kb.config import GTConfig  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.lifecycle import ProjectLifecycleService  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    """Create a temp project with a groundtruth.toml; return (root, config-file)."""
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _seed_phantom_fixture(db_path: Path) -> None:
    """Seed the four reconciliation cases.

    Case A (PROJECT-PROJECT-CANON-A): canonical active; phantom membership
        for WI-7001 has NO canonical equivalent -> T3 + T6 + T7.
    Case B (PROJECT-PROJECT-CANON-B): canonical RETIRED; phantom membership
        for WI-7002 has NO canonical equivalent -> T4 + DELIB-2506 path.
    Case C (PROJECT-PROJECT-CANON-C): canonical active; phantom AND canonical
        both have active membership for WI-7003 -> T5 (redundant case).
    Case D (PROJECT-PROJECT-CANON-MISSING): NO canonical exists; phantom has
        a membership for WI-7004 -> T10 (safety branch).
    """
    db = KnowledgeDB(db_path=db_path)
    try:
        service = ProjectLifecycleService(db)

        # ---- Case A: active canonical + phantom-only WI -----------------
        db.insert_project(
            name="CANON-A",
            id="PROJECT-CANON-A",
            changed_by="seed",
            change_reason="T3 fixture: canonical active",
        )
        db.insert_project(
            name="PROJECT-CANON-A",
            id="PROJECT-PROJECT-CANON-A",
            changed_by="seed",
            change_reason="T3 fixture: phantom for CANON-A",
        )
        db.insert_work_item(
            id="WI-7001",
            title="On phantom of active canonical only",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="seed",
            change_reason="T3 fixture WI",
        )
        db.link_project_work_item(
            project_id="PROJECT-PROJECT-CANON-A",
            work_item_id="WI-7001",
            changed_by="seed",
            change_reason="T3 fixture: phantom membership",
        )

        # ---- Case B: retired canonical + phantom-only WI (DELIB-2506) ---
        db.insert_project(
            name="CANON-B",
            id="PROJECT-CANON-B",
            changed_by="seed",
            change_reason="T4 fixture: canonical (about-to-retire)",
        )
        service.retire_project(
            "PROJECT-CANON-B",
            changed_by="seed",
            change_reason="T4 fixture: retire canonical pre-test",
        )
        db.insert_project(
            name="PROJECT-CANON-B",
            id="PROJECT-PROJECT-CANON-B",
            changed_by="seed",
            change_reason="T4 fixture: phantom for retired CANON-B",
        )
        db.insert_work_item(
            id="WI-7002",
            title="On phantom of retired canonical only",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="seed",
            change_reason="T4 fixture WI",
        )
        db.link_project_work_item(
            project_id="PROJECT-PROJECT-CANON-B",
            work_item_id="WI-7002",
            changed_by="seed",
            change_reason="T4 fixture: phantom membership",
        )

        # ---- Case C: active canonical + WI on BOTH (redundant case) -----
        db.insert_project(
            name="CANON-C",
            id="PROJECT-CANON-C",
            changed_by="seed",
            change_reason="T5 fixture: canonical active",
        )
        db.insert_project(
            name="PROJECT-CANON-C",
            id="PROJECT-PROJECT-CANON-C",
            changed_by="seed",
            change_reason="T5 fixture: phantom for CANON-C",
        )
        db.insert_work_item(
            id="WI-7003",
            title="On phantom AND canonical (redundant)",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="seed",
            change_reason="T5 fixture WI",
        )
        db.link_project_work_item(
            project_id="PROJECT-CANON-C",
            work_item_id="WI-7003",
            changed_by="seed",
            change_reason="T5 fixture: canonical (operator-applied) membership",
        )
        db.link_project_work_item(
            project_id="PROJECT-PROJECT-CANON-C",
            work_item_id="WI-7003",
            changed_by="seed",
            change_reason="T5 fixture: phantom membership",
        )

        # ---- Case D: phantom with NO canonical (safety branch) ----------
        db.insert_project(
            name="CANON-MISSING",
            id="PROJECT-PROJECT-CANON-MISSING",
            changed_by="seed",
            change_reason="T10 fixture: phantom with no canonical",
        )
        db.insert_work_item(
            id="WI-7004",
            title="On phantom with missing canonical",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="seed",
            change_reason="T10 fixture WI",
        )
        db.link_project_work_item(
            project_id="PROJECT-PROJECT-CANON-MISSING",
            work_item_id="WI-7004",
            changed_by="seed",
            change_reason="T10 fixture: phantom membership",
        )
    finally:
        db.close()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _config(root: Path) -> GTConfig:
    return GTConfig(
        db_path=root / "groundtruth.db",
        project_root=root,
    )


# ---------------------------------------------------------------------------
# Unit-level: phantom -> canonical id derivation
# ---------------------------------------------------------------------------


def test_canonical_id_derivation_strips_exactly_one_prefix() -> None:
    """The reverse of the doubling defect strips one PROJECT- prefix only."""
    assert _canonical_id_from_phantom("PROJECT-PROJECT-X") == "PROJECT-X"
    assert _canonical_id_from_phantom("PROJECT-PROJECT-GTKB-RELIABILITY-FIXES") == "PROJECT-GTKB-RELIABILITY-FIXES"
    # Triple-prefixed input would only collapse one level; the algorithm
    # explicitly does NOT regex-collapse arbitrary depth.
    assert _canonical_id_from_phantom("PROJECT-PROJECT-PROJECT-X") == "PROJECT-PROJECT-X"


# ---------------------------------------------------------------------------
# T1 — dry-run inventory matches seeded phantoms
# ---------------------------------------------------------------------------


def test_dry_run_inventory_matches_seeded_phantoms(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    report = build_reconcile_plan(_config(root), ReconcileRequest(apply=False))

    phantom_ids = sorted(e["plan"]["phantom_id"] for e in report["phantoms"])
    assert phantom_ids == [
        "PROJECT-PROJECT-CANON-A",
        "PROJECT-PROJECT-CANON-B",
        "PROJECT-PROJECT-CANON-C",
        "PROJECT-PROJECT-CANON-MISSING",
    ]
    by_id = {e["plan"]["phantom_id"]: e["plan"] for e in report["phantoms"]}
    assert by_id["PROJECT-PROJECT-CANON-A"]["canonical_id"] == "PROJECT-CANON-A"
    assert by_id["PROJECT-PROJECT-CANON-B"]["canonical_id"] == "PROJECT-CANON-B"
    assert by_id["PROJECT-PROJECT-CANON-C"]["canonical_id"] == "PROJECT-CANON-C"
    assert by_id["PROJECT-PROJECT-CANON-MISSING"]["canonical_id"] == "PROJECT-CANON-MISSING"
    # Case A: needs new canonical link for WI-7001.
    assert by_id["PROJECT-PROJECT-CANON-A"]["canonical_links_to_create"] == ["WI-7001"]
    # Case C: NO new canonical link (redundant).
    assert by_id["PROJECT-PROJECT-CANON-C"]["canonical_links_to_create"] == []


# ---------------------------------------------------------------------------
# T2 — dry-run makes no DB writes
# ---------------------------------------------------------------------------


def test_dry_run_makes_no_db_writes(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")
    db_path = root / "groundtruth.db"

    before = _file_hash(db_path)
    build_reconcile_plan(_config(root), ReconcileRequest(apply=False))
    after = _file_hash(db_path)

    assert before == after, "dry-run must not mutate groundtruth.db"


# ---------------------------------------------------------------------------
# T3 — apply links a WI whose canonical project is active and lacks the link
# ---------------------------------------------------------------------------


def test_apply_links_missing_canonical_active(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        canonical_a = db.list_project_work_items("PROJECT-CANON-A", include_inactive=False)
        canonical_a_wis = {str(m["work_item_id"]) for m in canonical_a}
    finally:
        db.close()
    assert "WI-7001" in canonical_a_wis, (
        "Case A: canonical PROJECT-CANON-A should now have an active membership for WI-7001 after --apply."
    )


# ---------------------------------------------------------------------------
# T4 — apply links a WI whose canonical project is RETIRED (DELIB-2506)
# ---------------------------------------------------------------------------


def test_apply_links_missing_canonical_retired(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        canonical_b = db.list_project_work_items("PROJECT-CANON-B", include_inactive=False)
        canonical_b_wis = {str(m["work_item_id"]) for m in canonical_b}
        canonical_b_project = db.get_project("PROJECT-CANON-B")
    finally:
        db.close()
    assert "WI-7002" in canonical_b_wis, (
        "Case B: active membership for WI-7002 should be created on "
        "RETIRED canonical PROJECT-CANON-B per DELIB-2506 disposition."
    )
    # The retired canonical stays retired; this thread does NOT reactivate it.
    assert str(canonical_b_project["status"]) == "retired"


# ---------------------------------------------------------------------------
# T5 — apply does NOT create duplicate canonical membership (redundant case)
# ---------------------------------------------------------------------------


def test_apply_skips_redundant_canonical_link(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    # Count the canonical's active memberships for WI-7003 before AND after.
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        before = [
            m
            for m in db.list_project_work_items("PROJECT-CANON-C", include_inactive=False)
            if str(m["work_item_id"]) == "WI-7003"
        ]
    finally:
        db.close()
    assert len(before) == 1, "fixture sanity: canonical-C has one active WI-7003 membership"

    build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        after = [
            m
            for m in db.list_project_work_items("PROJECT-CANON-C", include_inactive=False)
            if str(m["work_item_id"]) == "WI-7003"
        ]
    finally:
        db.close()
    assert len(after) == 1, (
        "Case C: redundant canonical membership must not be duplicated; "
        "still exactly one active row for WI-7003 on PROJECT-CANON-C."
    )


# ---------------------------------------------------------------------------
# T6 — apply supersedes each phantom membership row
# ---------------------------------------------------------------------------


def test_apply_supersedes_phantom_membership(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        # Each phantom (A, B, C; not MISSING — it gets skipped) had one
        # active membership. After apply, those rows should be superseded.
        for phantom_id, wi_id in (
            ("PROJECT-PROJECT-CANON-A", "WI-7001"),
            ("PROJECT-PROJECT-CANON-B", "WI-7002"),
            ("PROJECT-PROJECT-CANON-C", "WI-7003"),
        ):
            actives = [
                m
                for m in db.list_project_work_items(phantom_id, include_inactive=False)
                if str(m["work_item_id"]) == wi_id
            ]
            assert actives == [], (
                f"{phantom_id}: phantom membership for {wi_id} must be superseded (no active rows after --apply)."
            )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# T7 — apply retires each phantom project
# ---------------------------------------------------------------------------


def test_apply_retires_phantom_project(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        statuses = {
            phantom_id: str(db.get_project(phantom_id)["status"])
            for phantom_id in (
                "PROJECT-PROJECT-CANON-A",
                "PROJECT-PROJECT-CANON-B",
                "PROJECT-PROJECT-CANON-C",
                "PROJECT-PROJECT-CANON-MISSING",
            )
        }
    finally:
        db.close()
    assert statuses["PROJECT-PROJECT-CANON-A"] == "retired"
    assert statuses["PROJECT-PROJECT-CANON-B"] == "retired"
    assert statuses["PROJECT-PROJECT-CANON-C"] == "retired"
    # MISSING-canonical phantom is SKIPPED, so it remains active (no retirement).
    assert statuses["PROJECT-PROJECT-CANON-MISSING"] == "active"


# ---------------------------------------------------------------------------
# T8 — apply is idempotent on rerun
# ---------------------------------------------------------------------------


def test_apply_idempotent_on_rerun(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    db_path = root / "groundtruth.db"
    before = _file_hash(db_path)
    report2 = build_reconcile_plan(_config(root), ReconcileRequest(apply=True))
    after = _file_hash(db_path)

    # Second-pass apply made zero changes -> the db file is byte-identical.
    assert before == after, "rerun must be a true no-op; no second-pass MemBase writes"
    totals = report2["totals"]
    assert totals["canonical_links_created"] == 0
    assert totals["phantom_memberships_superseded"] == 0
    assert totals["phantom_projects_retired"] == 0


# ---------------------------------------------------------------------------
# T9 — apply --json emits structured report with reconciliation counts
# ---------------------------------------------------------------------------


def test_apply_json_report_shape(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "projects",
            "reconcile-doubled-prefix",
            "--apply",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    report = json.loads(result.output)
    assert report["apply"] is True
    assert set(report["totals"]) == {
        "phantom_count",
        "skipped_count",
        "canonical_links_created",
        "phantom_memberships_superseded",
        "phantom_projects_retired",
    }
    assert report["totals"]["phantom_count"] == 4
    assert report["totals"]["skipped_count"] == 1  # MISSING canonical
    assert report["totals"]["canonical_links_created"] == 2  # Cases A + B
    assert report["totals"]["phantom_memberships_superseded"] == 3  # A + B + C
    assert report["totals"]["phantom_projects_retired"] == 3  # A + B + C
    # Per-phantom plan shape is locked.
    for entry in report["phantoms"]:
        plan = entry["plan"]
        assert plan["phantom_id"].startswith(PHANTOM_PREFIX)
        assert "results" in entry  # only present in apply mode


# ---------------------------------------------------------------------------
# T10 — phantom with missing canonical is skipped + reported
# ---------------------------------------------------------------------------


def test_phantom_with_missing_canonical_is_skipped(tmp_path: Path) -> None:
    root, _ = _project(tmp_path)
    _seed_phantom_fixture(root / "groundtruth.db")

    report = build_reconcile_plan(_config(root), ReconcileRequest(apply=True))

    missing = next(e["plan"] for e in report["phantoms"] if e["plan"]["phantom_id"] == "PROJECT-PROJECT-CANON-MISSING")
    assert missing["skipped"] is True
    assert missing["skip_reason"] == "canonical_missing"
    assert missing["canonical_present"] is False
    # No mutations attempted on the skipped phantom.
    missing_results = next(
        e["results"] for e in report["phantoms"] if e["plan"]["phantom_id"] == "PROJECT-PROJECT-CANON-MISSING"
    )
    assert missing_results["canonical_links_created"] == []
    assert missing_results["phantom_memberships_superseded"] == []
    assert missing_results["phantom_retired"] is False
