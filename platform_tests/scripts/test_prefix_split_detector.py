"""Tests for the Stage 1 prefix-split detector.

Covers detection structure (3 named fields), live-shape fidelity, the
load-bearing post-apply structural invariants (per Codex -004 GO required
implementation notes 1 and 2), strict apply-order discipline, refusal guards,
read-only no-mutation in default mode, determinism, and idempotency.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from scripts.hygiene import prefix_split_detector  # noqa: E402

# ---------------------------------------------------------------------------
# Read-only fixture: minimal tables matching the two views the detector reads.
# Used by default-mode tests that don't need the full KnowledgeDB schema.
# ---------------------------------------------------------------------------


def _build_ro_fixture(tmp_path: Path, projects, memberships) -> Path:
    """Build a minimal DB matching the read shape (current_projects + memberships view)."""
    db = tmp_path / "groundtruth.db"
    con = sqlite3.connect(db)
    try:
        con.execute("CREATE TABLE current_projects (id TEXT, status TEXT)")
        con.executemany("INSERT INTO current_projects VALUES (?, ?)", projects)
        con.execute(
            "CREATE TABLE current_project_work_item_memberships "
            "(id TEXT, work_item_id TEXT, project_id TEXT, status TEXT)"
        )
        con.executemany(
            "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?, ?)",
            memberships,
        )
        con.commit()
    finally:
        con.close()
    return db


def _pwm_id(project_id: str, wi_id: str) -> str:
    return f"PWM-{project_id}-{wi_id}"


@pytest.fixture
def overlap_fixture(tmp_path):
    """Mirror the live prefix-split case: 8 overlapping items + 2 canonical-only.

    Per the Codex -002 NO-GO P1 observation: ``GTKB-V1-RELEASE-STRATEGY-001``
    and ``PROJECT-GTKB-V1-RELEASE-STRATEGY-001`` are BOTH active; the 8 items
    WI-3400..WI-3407 are active on both; canonical has 2 canonical-only items.
    """
    non_can = "GTKB-V1-RELEASE-STRATEGY-001"
    can = "PROJECT-GTKB-V1-RELEASE-STRATEGY-001"
    projects = [(non_can, "active"), (can, "active"), ("PROJECT-UNRELATED", "active")]
    memberships = []
    for i in range(8):
        wi = f"WI-340{i}"
        memberships.append((_pwm_id(non_can, wi), wi, non_can, "active"))
        memberships.append((_pwm_id(can, wi), wi, can, "active"))
    # Canonical-only items
    for wi in ("WI-3395", "WI-4303"):
        memberships.append((_pwm_id(can, wi), wi, can, "active"))
    # Unrelated single-project item (must not appear in plan)
    memberships.append((_pwm_id("PROJECT-UNRELATED", "WI-9999"), "WI-9999", "PROJECT-UNRELATED", "active"))
    return _build_ro_fixture(tmp_path, projects, memberships)


# ---------------------------------------------------------------------------
# Default-mode (read-only) tests
# ---------------------------------------------------------------------------


def test_detect_emits_three_named_fields(overlap_fixture):
    plan = prefix_split_detector.detect(overlap_fixture)
    assert "pairs" in plan
    assert len(plan["pairs"]) == 1
    pair = plan["pairs"][0]
    for field in (
        "canonical_id",
        "non_canonical_id",
        "canonical_links_to_create",
        "non_canonical_memberships_to_deactivate",
        "non_canonical_project_to_retire",
    ):
        assert field in pair, f"missing field {field!r}"


def test_detect_live_shape_fidelity(overlap_fixture):
    """The 8-overlap case must produce canonical_links_to_create=[]."""
    plan = prefix_split_detector.detect(overlap_fixture)
    pair = plan["pairs"][0]
    assert pair["canonical_id"] == "PROJECT-GTKB-V1-RELEASE-STRATEGY-001"
    assert pair["non_canonical_id"] == "GTKB-V1-RELEASE-STRATEGY-001"
    assert pair["canonical_links_to_create"] == []
    assert len(pair["non_canonical_memberships_to_deactivate"]) == 8
    deactivate_wis = [e["work_item_id"] for e in pair["non_canonical_memberships_to_deactivate"]]
    assert deactivate_wis == [f"WI-340{i}" for i in range(8)]
    assert pair["non_canonical_project_to_retire"] is True


def test_unrelated_single_projects_not_in_plan(overlap_fixture):
    """A project with no prefix-split partner must not appear as a pair."""
    plan = prefix_split_detector.detect(overlap_fixture)
    pair_ids = {p["non_canonical_id"] for p in plan["pairs"]} | {p["canonical_id"] for p in plan["pairs"]}
    assert "PROJECT-UNRELATED" not in pair_ids


def test_detect_canonical_only_subset(tmp_path):
    """If only one of the two id forms is active, it is NOT a pair."""
    db = _build_ro_fixture(
        tmp_path,
        projects=[
            ("GTKB-FOO", "active"),
            ("PROJECT-GTKB-FOO", "retired"),  # retired -- only one is active
        ],
        memberships=[],
    )
    plan = prefix_split_detector.detect(db)
    assert plan["pairs"] == []


def test_canonical_links_to_create_populated_when_non_overlap(tmp_path):
    """If non-canonical has items NOT on canonical, they appear in canonical_links_to_create."""
    non_can = "GTKB-NONOVERLAP"
    can = "PROJECT-GTKB-NONOVERLAP"
    memberships = [
        (_pwm_id(non_can, "WI-100"), "WI-100", non_can, "active"),
        (_pwm_id(non_can, "WI-101"), "WI-101", non_can, "active"),
        (_pwm_id(can, "WI-100"), "WI-100", can, "active"),  # overlap on WI-100 only
    ]
    db = _build_ro_fixture(
        tmp_path,
        projects=[(non_can, "active"), (can, "active")],
        memberships=memberships,
    )
    plan = prefix_split_detector.detect(db)
    pair = plan["pairs"][0]
    assert pair["canonical_links_to_create"] == ["WI-101"]
    assert len(pair["non_canonical_memberships_to_deactivate"]) == 2


def test_default_mode_determinism(overlap_fixture):
    a = json.dumps(prefix_split_detector.detect(overlap_fixture), sort_keys=True)
    b = json.dumps(prefix_split_detector.detect(overlap_fixture), sort_keys=True)
    assert a == b


def test_default_mode_no_mutation_row_counts(overlap_fixture):
    con = sqlite3.connect(overlap_fixture)
    before_projects = con.execute("SELECT COUNT(*) FROM current_projects").fetchone()[0]
    before_memberships = con.execute("SELECT COUNT(*) FROM current_project_work_item_memberships").fetchone()[0]
    con.close()
    prefix_split_detector.detect(overlap_fixture)
    con = sqlite3.connect(overlap_fixture)
    after_projects = con.execute("SELECT COUNT(*) FROM current_projects").fetchone()[0]
    after_memberships = con.execute("SELECT COUNT(*) FROM current_project_work_item_memberships").fetchone()[0]
    con.close()
    assert before_projects == after_projects
    assert before_memberships == after_memberships


def test_default_mode_no_write_paths_in_detect_ast():
    """AST scan: the default ``detect()`` path must have no mutation calls."""
    source = Path(prefix_split_detector.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    detect_func = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "detect")
    forbidden_attrs = {"commit", "executescript", "executemany", "insert_project", "link_project_work_item"}
    for node in ast.walk(detect_func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in forbidden_attrs, f"detect() calls forbidden {node.func.attr}"
    assert "mode=ro" in source, "detector must use read-only SQLite URI"


def test_cli_default_mode_emits_json(overlap_fixture):
    """The CLI entry point in default mode must emit valid JSON to stdout."""
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "hygiene" / "prefix_split_detector.py"),
            "--db",
            str(overlap_fixture),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"CLI failed: {proc.stderr}"
    payload = json.loads(proc.stdout)
    assert len(payload["pairs"]) == 1


# ---------------------------------------------------------------------------
# Refusal-guard tests (apply-path argument validation)
# ---------------------------------------------------------------------------


def test_apply_refuses_without_canonical_arg(tmp_path):
    db = tmp_path / "groundtruth.db"
    db.touch()
    with pytest.raises(SystemExit) as excinfo:
        prefix_split_detector.main(["--db", str(db), "--apply", "--merge-from", "X", "--auq-id", "AUQ-1"])
    assert "specify the pair" in str(excinfo.value) or "--canonical" in str(excinfo.value)


def test_apply_refuses_without_merge_from_arg(tmp_path):
    db = tmp_path / "groundtruth.db"
    db.touch()
    with pytest.raises(SystemExit) as excinfo:
        prefix_split_detector.main(["--db", str(db), "--apply", "--canonical", "PROJECT-X", "--auq-id", "AUQ-1"])
    assert "specify the pair" in str(excinfo.value) or "--canonical" in str(excinfo.value)


def test_apply_refuses_without_auq_id(tmp_path):
    db = tmp_path / "groundtruth.db"
    db.touch()
    with pytest.raises(SystemExit) as excinfo:
        prefix_split_detector.main(["--db", str(db), "--apply", "--canonical", "PROJECT-X", "--merge-from", "X"])
    assert "auq-id" in str(excinfo.value).lower() or "AskUserQuestion" in str(excinfo.value)


def test_apply_refuses_on_unknown_pair(overlap_fixture):
    """An owner-supplied pair not in the live dry-run set must be refused."""
    with pytest.raises(SystemExit) as excinfo:
        prefix_split_detector.apply(
            overlap_fixture,
            canonical_id="PROJECT-DOES-NOT-EXIST",
            non_canonical_id="DOES-NOT-EXIST",
            auq_id="AUQ-TEST",
            changed_by="test/claude",
        )
    assert "not in the live active-BOTH" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Post-apply structural-invariant tests (Codex GO required implementation notes)
# ---------------------------------------------------------------------------


@pytest.fixture
def kb_fixture(tmp_path):
    """Build a real KnowledgeDB-backed fixture so the apply path can run."""
    from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415

    db_path = tmp_path / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)

    non_can = "GTKB-V1-RELEASE-STRATEGY-001"
    can = "PROJECT-GTKB-V1-RELEASE-STRATEGY-001"

    db.insert_project(
        id=non_can,
        name="non-canonical",
        changed_by="test/seed",
        change_reason="seed prefix-split fixture",
    )
    db.insert_project(
        id=can,
        name="canonical",
        changed_by="test/seed",
        change_reason="seed prefix-split fixture",
    )
    # Seed work items + dual memberships matching the live overlap shape.
    for i in range(8):
        wi = f"WI-340{i}"
        db.insert_work_item(
            id=wi,
            title=f"test {wi}",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test/seed",
            change_reason="seed prefix-split fixture",
        )
        db.link_project_work_item(
            project_id=non_can,
            work_item_id=wi,
            changed_by="test/seed",
            change_reason="seed non-canonical membership",
        )
        db.link_project_work_item(
            project_id=can,
            work_item_id=wi,
            changed_by="test/seed",
            change_reason="seed canonical membership",
        )
    return db_path, non_can, can


def _active_count(db_path: Path, project_id: str) -> int:
    con = sqlite3.connect(str(db_path))
    try:
        return con.execute(
            "SELECT COUNT(*) FROM current_project_work_item_memberships WHERE project_id = ? AND status = 'active'",
            (project_id,),
        ).fetchone()[0]
    finally:
        con.close()


def _project_status_query(db_path: Path, project_id: str) -> str | None:
    con = sqlite3.connect(str(db_path))
    try:
        row = con.execute("SELECT status FROM current_projects WHERE id = ?", (project_id,)).fetchone()
        return row[0] if row else None
    finally:
        con.close()


def test_apply_no_duplicate_active_canonical_memberships(kb_fixture):
    """Codex GO required note 2: no duplicate active canonical membership per WI."""
    db_path, non_can, can = kb_fixture
    prefix_split_detector.apply(
        db_path,
        canonical_id=can,
        non_canonical_id=non_can,
        auq_id="AUQ-TEST-1",
        changed_by="test/claude",
    )
    con = sqlite3.connect(str(db_path))
    try:
        for i in range(8):
            wi = f"WI-340{i}"
            n = con.execute(
                "SELECT COUNT(*) FROM current_project_work_item_memberships "
                "WHERE project_id = ? AND work_item_id = ? AND status = 'active'",
                (can, wi),
            ).fetchone()[0]
            assert n == 1, f"{wi}: expected exactly 1 active canonical membership, got {n}"
    finally:
        con.close()


def test_apply_all_non_canonical_memberships_deactivated(kb_fixture):
    """All 8 non-canonical active memberships must become non-active."""
    db_path, non_can, _ = kb_fixture
    prefix_split_detector.apply(
        db_path,
        canonical_id=f"PROJECT-{non_can}" if not non_can.startswith("PROJECT-") else non_can,
        non_canonical_id=non_can,
        auq_id="AUQ-TEST-2",
        changed_by="test/claude",
    )
    assert _active_count(db_path, non_can) == 0


def test_apply_retires_non_canonical_project(kb_fixture):
    db_path, non_can, can = kb_fixture
    prefix_split_detector.apply(
        db_path,
        canonical_id=can,
        non_canonical_id=non_can,
        auq_id="AUQ-TEST-3",
        changed_by="test/claude",
    )
    assert _project_status_query(db_path, non_can) == "retired"


def test_retired_non_canonical_project_has_zero_active_memberships(kb_fixture):
    """Codex GO required note 1: THE load-bearing structural invariant.

    After apply, the retired non-canonical project must have zero active
    memberships pointing at it. This is the test that closes the structural
    defect class Stage 1 exists to repair.
    """
    db_path, non_can, can = kb_fixture
    prefix_split_detector.apply(
        db_path,
        canonical_id=can,
        non_canonical_id=non_can,
        auq_id="AUQ-TEST-4",
        changed_by="test/claude",
    )
    assert _project_status_query(db_path, non_can) == "retired"
    assert _active_count(db_path, non_can) == 0


def test_apply_idempotent_on_rerun(kb_fixture):
    """A second --apply on an already-completed pair writes zero new versions."""
    db_path, non_can, can = kb_fixture
    prefix_split_detector.apply(
        db_path, canonical_id=can, non_canonical_id=non_can, auq_id="AUQ-FIRST", changed_by="test/claude"
    )
    con = sqlite3.connect(str(db_path))
    try:
        version_count_before = con.execute(
            "SELECT COUNT(*) FROM project_work_item_memberships WHERE project_id = ?", (non_can,)
        ).fetchone()[0]
    finally:
        con.close()
    # Second run: pair no longer in dry-run (non-canonical retired); refuses.
    with pytest.raises(SystemExit) as excinfo:
        prefix_split_detector.apply(
            db_path,
            canonical_id=can,
            non_canonical_id=non_can,
            auq_id="AUQ-SECOND",
            changed_by="test/claude",
        )
    assert "not in the live active-BOTH" in str(excinfo.value)
    con = sqlite3.connect(str(db_path))
    try:
        version_count_after = con.execute(
            "SELECT COUNT(*) FROM project_work_item_memberships WHERE project_id = ?", (non_can,)
        ).fetchone()[0]
    finally:
        con.close()
    assert version_count_before == version_count_after
