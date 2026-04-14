# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for F8: Provenance Reconciliation.

27 tests organized into 5 sections, per:

    - bridge/gtkb-phase4-implementation-007.md (lines 216-253)
    - bridge/gtkb-phase4-implementation-009.md (lines 126-176, corrected
      expired-provisional field contract)
    - bridge/gtkb-phase4-implementation-010.md (GO verdict)

Section layout:

    Orphan Detection                (12 tests)
    Plain-Text Assertion Safety      (3 tests)
    Authority Conflicts              (3 tests)
    Stale Detection                  (6 tests)
    Provenance                       (3 tests)

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.reconciliation import (
    ReconciliationReport,
    find_authority_conflicts,
    find_duplicate_specs,
    find_expired_provisionals,
    find_orphaned_assertions,
    find_stale_specs,
)

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB without governance gates (plain-text assertions)."""
    return KnowledgeDB(db_path=tmp_path / "recon.db")


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Project root used for orphan resolution.

    Creates an empty ``src/`` directory but intentionally does NOT seed any
    files — individual tests opt in to specific files.
    """
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    return root


def _touch(root: Path, rel: str) -> None:
    """Create an empty file at ``root / rel`` (making parents as needed)."""
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("")


def _insert_spec(
    db: KnowledgeDB,
    spec_id: str,
    *,
    assertions: list | None = None,
    section: str | None = "default",
    scope: str | None = None,
    authority: str = "stated",
    status: str = "specified",
    title: str | None = None,
    provisional_until: str | None = None,
) -> None:
    """Shared spec-insert helper.

    Uses ``validate_assertions=False`` so tests may seed plain-text
    assertions that are valid per the assertion schema but would otherwise
    be rejected if mixed inside dict-children with bad fields.
    """
    db.insert_spec(
        id=spec_id,
        title=title or f"Spec {spec_id}",
        status=status,
        changed_by="test",
        change_reason="test seed",
        section=section,
        scope=scope,
        assertions=assertions,
        authority=authority,
        provisional_until=provisional_until,
        validate_assertions=False,
    )


def _set_spec_changed_at(db: KnowledgeDB, spec_id: str, iso: str) -> None:
    """Overwrite the ``changed_at`` timestamp on every version of a spec."""
    conn = db._get_conn()
    conn.execute(
        "UPDATE specifications SET changed_at = ? WHERE id = ?",
        (iso, spec_id),
    )
    conn.commit()


def _insert_snapshot(db: KnowledgeDB, session_id: str, iso: str) -> None:
    """Insert a synthetic snapshot row with an explicit ``captured_at``.

    Bypasses :meth:`KnowledgeDB.capture_session_snapshot` because that
    API always stamps the row with ``_now()``.  The stored ``data`` is
    a tiny JSON blob — F8 stale detection only reads ``captured_at``.
    """
    conn = db._get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO session_snapshots (session_id, captured_at, data) VALUES (?, ?, ?)",
        (session_id, iso, "{}"),
    )
    conn.commit()


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


# ===========================================================================
# Section 1: Orphan Detection (12 tests)
# ===========================================================================


class TestOrphanDetection:
    """Orphan detection reuses the shared assertion-target extractor."""

    # 1
    def test_grep_literal_exists_not_orphaned(self, db, project_root):
        _touch(project_root, "src/app.py")
        _insert_spec(
            db,
            "SPEC-1",
            assertions=[{"type": "grep", "file": "src/app.py", "pattern": "def"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert report.findings == []

    # 2
    def test_grep_literal_missing_orphaned(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-1",
            assertions=[{"type": "grep", "file": "src/missing.py", "pattern": "x"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding["spec_id"] == "SPEC-1"
        assert finding["assertion_type"] == "grep"
        assert finding["file_target"] == "src/missing.py"

    # 3 — alias: `path` in place of `file`
    def test_grep_path_alias(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-2",
            assertions=[{"type": "grep", "path": "src/ghost.py", "pattern": "x"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["file_target"] == "src/ghost.py"

    # 4 — alias: `target` in place of `file`
    def test_grep_target_alias(self, db, project_root):
        _touch(project_root, "src/real.py")
        _insert_spec(
            db,
            "SPEC-3",
            assertions=[{"type": "grep", "target": "src/real.py", "pattern": "x"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert report.findings == []

    # 5
    def test_glob_assertion_with_matches_not_orphaned(self, db, project_root):
        _touch(project_root, "src/a.py")
        _touch(project_root, "src/b.py")
        _insert_spec(
            db,
            "SPEC-4",
            assertions=[{"type": "glob", "pattern": "src/*.py"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert report.findings == []

    # 6
    def test_glob_zero_matches_orphaned(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-5",
            assertions=[{"type": "glob", "pattern": "src/ghosts/*.py"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding["assertion_type"] == "glob"
        assert finding["file_target"] == "src/ghosts/*.py"
        assert finding["file_is_glob"] is True

    # 7
    def test_grep_file_glob_with_matches_not_orphaned(self, db, project_root):
        _touch(project_root, "src/one.py")
        _insert_spec(
            db,
            "SPEC-6",
            assertions=[{"type": "grep", "file": "src/*.py", "pattern": "def"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert report.findings == []

    # 8
    def test_grep_file_glob_zero_matches_orphaned(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-7",
            assertions=[{"type": "grep", "file": "src/none/*.py", "pattern": "def"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "grep"
        assert report.findings[0]["file_is_glob"] is True

    # 9
    def test_grep_absent_file_glob_zero_matches_orphaned(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-8",
            assertions=[
                {
                    "type": "grep_absent",
                    "file": "src/missing/*.py",
                    "pattern": "BAD",
                }
            ],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "grep_absent"

    # 10
    def test_count_file_glob_zero_matches_orphaned(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-9",
            assertions=[
                {
                    "type": "count",
                    "file": "src/vanished/*.py",
                    "pattern": "TODO",
                    "operator": ">=",
                    "expected": 1,
                }
            ],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "count"

    # 11 — file_exists with `*` in name → literal resolution path
    def test_file_exists_literal_star_orphaned(self, db, project_root):
        # file_exists does NOT treat `*` as a glob; the literal filename
        # containing an asterisk cannot exist as a real file, so the
        # detector must report it as orphaned via the literal-resolve path.
        _insert_spec(
            db,
            "SPEC-10",
            assertions=[{"type": "file_exists", "file": "src/a*b.py"}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "file_exists"
        assert report.findings[0]["file_target"] == "src/a*b.py"
        assert report.findings[0]["file_is_glob"] is False

    # 12 — composition: mixed children → per-child reporting
    def test_all_of_composition_mixed_children(self, db, project_root):
        _touch(project_root, "src/keep.py")
        _insert_spec(
            db,
            "SPEC-11",
            assertions=[
                {
                    "type": "all_of",
                    "assertions": [
                        {
                            "type": "grep",
                            "file": "src/keep.py",
                            "pattern": "def",
                        },
                        {
                            "type": "grep",
                            "file": "src/gone.py",
                            "pattern": "def",
                        },
                    ],
                }
            ],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        # Only the second leaf is orphaned → exactly one finding.
        assert len(report.findings) == 1
        assert report.findings[0]["file_target"] == "src/gone.py"
        assert report.findings[0]["spec_id"] == "SPEC-11"


# ===========================================================================
# Section 2: Plain-Text Assertion Safety (3 tests)
# ===========================================================================


class TestPlainTextAssertionSafety:
    """Plain-text (non-dict) assertion children must be silently skipped."""

    # 13
    def test_top_level_plain_text_skipped(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-TXT-1",
            assertions=["All forms must be WCAG 2.1 AA compliant."],
        )
        # Must not crash and must not produce any finding for the text.
        report = find_orphaned_assertions(db, project_root=project_root)
        assert report.findings == []
        assert isinstance(report, ReconciliationReport)

    # 14
    def test_all_of_with_plain_text_child(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-TXT-2",
            assertions=[
                {
                    "type": "all_of",
                    "assertions": [
                        "Owner review required",
                        {"type": "grep", "file": "src/bye.py", "pattern": "x"},
                    ],
                }
            ],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        # Text child silently dropped; dict child produces a single
        # orphan finding (the file does not exist).
        assert len(report.findings) == 1
        assert report.findings[0]["file_target"] == "src/bye.py"

    # 15
    def test_non_machine_dict_child_skipped(self, db, project_root):
        _insert_spec(
            db,
            "SPEC-TXT-3",
            assertions=[{"type": "visual", "description": "Widget renders red button."}],
        )
        report = find_orphaned_assertions(db, project_root=project_root)
        # Unknown type -> extractor drops it, no orphan finding.
        assert report.findings == []


# ===========================================================================
# Section 3: Authority Conflicts (3 tests)
# ===========================================================================


class TestAuthorityConflicts:
    """Stated-vs-inferred structural overlap within the same section/scope."""

    # 16 — alias overlap (different alias keys, same resolved file_target)
    def test_alias_overlap(self, db):
        _insert_spec(
            db,
            "SPEC-S",
            section="auth",
            scope="login",
            authority="stated",
            assertions=[{"type": "grep", "file": "src/auth.py", "pattern": "login"}],
        )
        _insert_spec(
            db,
            "SPEC-I",
            section="auth",
            scope="login",
            authority="inferred",
            assertions=[{"type": "grep", "path": "src/auth.py", "pattern": "login"}],
        )
        report = find_authority_conflicts(db)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding["stated_spec"] == "SPEC-S"
        assert finding["inferred_spec"] == "SPEC-I"
        assert "src/auth.py" in finding["overlapping_targets"]

    # 17 — composition overlap
    def test_composition_overlap(self, db):
        _insert_spec(
            db,
            "SPEC-STATED",
            section="billing",
            scope="invoice",
            authority="stated",
            assertions=[
                {
                    "type": "all_of",
                    "assertions": [
                        {
                            "type": "grep",
                            "file": "src/bill.py",
                            "pattern": "invoice",
                        }
                    ],
                }
            ],
        )
        _insert_spec(
            db,
            "SPEC-INFERRED",
            section="billing",
            scope="invoice",
            authority="inferred",
            assertions=[{"type": "grep", "file": "src/bill.py", "pattern": "pay"}],
        )
        report = find_authority_conflicts(db)
        assert len(report.findings) == 1
        assert report.findings[0]["overlapping_targets"] == ["src/bill.py"]

    # 18 — glob-string overlap
    def test_glob_string_overlap(self, db):
        _insert_spec(
            db,
            "SPEC-GS",
            section="widget",
            scope="ui",
            authority="stated",
            assertions=[{"type": "glob", "pattern": "src/widgets/*.tsx"}],
        )
        _insert_spec(
            db,
            "SPEC-GI",
            section="widget",
            scope="ui",
            authority="inferred",
            assertions=[{"type": "glob", "pattern": "src/widgets/*.tsx"}],
        )
        report = find_authority_conflicts(db)
        assert len(report.findings) == 1
        assert "src/widgets/*.tsx" in report.findings[0]["overlapping_targets"]


# ===========================================================================
# Section 4: Stale Detection (6 tests)
# ===========================================================================


class TestStaleDetection:
    """Snapshot-backed primary path + changed_at fallback."""

    # 19 — snapshot-backed positive (activity inside evidence window)
    def test_stale_from_snapshots_with_section_activity(self, db):
        base = datetime(2026, 1, 1, tzinfo=UTC)
        # Target spec frozen at day 1
        _insert_spec(db, "SPEC-OLD", section="core")
        _set_spec_changed_at(db, "SPEC-OLD", _iso(base + timedelta(days=1)))

        # 5 snapshots at days 10, 20, 30, 40, 50 — all after day 1.
        # Window = [day 10 (oldest of N), day 50 (most recent)].
        for i, day in enumerate([10, 20, 30, 40, 50]):
            _insert_snapshot(db, f"S{i}", _iso(base + timedelta(days=day)))

        # Another spec in same section touched at day 25 — INSIDE the
        # evidence window (day 25 > T_window_start = day 10).
        _insert_spec(db, "SPEC-YOUNG", section="core")
        _set_spec_changed_at(db, "SPEC-YOUNG", _iso(base + timedelta(days=25)))

        report = find_stale_specs(db, staleness_threshold_sessions=5)
        ids = [f["spec_id"] for f in report.findings]
        assert "SPEC-OLD" in ids
        assert "SPEC-YOUNG" not in ids  # the active spec itself isn't stale
        old_finding = next(f for f in report.findings if f["spec_id"] == "SPEC-OLD")
        assert old_finding["reason"] == "snapshot_window"

    # 20 — snapshot-backed negative (section entirely quiet)
    def test_stale_from_snapshots_without_section_activity(self, db):
        base = datetime(2026, 1, 1, tzinfo=UTC)
        _insert_spec(db, "SPEC-ALONE", section="quiet")
        _set_spec_changed_at(db, "SPEC-ALONE", _iso(base + timedelta(days=1)))

        for i, day in enumerate([10, 20, 30, 40, 50]):
            _insert_snapshot(db, f"S{i}", _iso(base + timedelta(days=day)))

        report = find_stale_specs(db, staleness_threshold_sessions=5)
        ids = [f["spec_id"] for f in report.findings]
        assert "SPEC-ALONE" not in ids

    # 21 — NEW: activity BEFORE the evidence window → NOT reported
    def test_stale_from_snapshots_activity_BEFORE_window(self, db):
        base = datetime(2026, 1, 1, tzinfo=UTC)
        _insert_spec(db, "SPEC-OLD", section="archive")
        _set_spec_changed_at(db, "SPEC-OLD", _iso(base + timedelta(days=1)))

        # Other spec touched at day 2 — BEFORE window_start = day 10.
        _insert_spec(db, "SPEC-OTHER", section="archive")
        _set_spec_changed_at(db, "SPEC-OTHER", _iso(base + timedelta(days=2)))

        # 5 snapshots at days 10, 20, 30, 40, 50 → window_start = day 10.
        for i, day in enumerate([10, 20, 30, 40, 50]):
            _insert_snapshot(db, f"S{i}", _iso(base + timedelta(days=day)))

        report = find_stale_specs(db, staleness_threshold_sessions=5)
        ids = [f["spec_id"] for f in report.findings]
        # day 2 is NOT inside [day 10, now] → must NOT be reported stale.
        assert "SPEC-OLD" not in ids

    # 22 — fallback positive
    def test_stale_fallback_with_section_activity(self, db):
        now = datetime.now(UTC)
        _insert_spec(db, "SPEC-AGED", section="fallback")
        _set_spec_changed_at(db, "SPEC-AGED", _iso(now - timedelta(days=120)))

        _insert_spec(db, "SPEC-FRESH", section="fallback")
        _set_spec_changed_at(db, "SPEC-FRESH", _iso(now - timedelta(days=5)))
        # No snapshots at all → fallback path runs.
        report = find_stale_specs(db, staleness_threshold_sessions=5)
        ids = [f["spec_id"] for f in report.findings]
        assert "SPEC-AGED" in ids
        aged = next(f for f in report.findings if f["spec_id"] == "SPEC-AGED")
        assert aged["reason"] == "changed_at_fallback"

    # 23 — fallback negative
    def test_stale_fallback_no_section_activity(self, db):
        now = datetime.now(UTC)
        _insert_spec(db, "SPEC-AGED", section="dormant")
        _set_spec_changed_at(db, "SPEC-AGED", _iso(now - timedelta(days=120)))

        # Same-section activity happened 200 days ago → NOT within 30 days.
        _insert_spec(db, "SPEC-ALSO-OLD", section="dormant")
        _set_spec_changed_at(db, "SPEC-ALSO-OLD", _iso(now - timedelta(days=200)))
        report = find_stale_specs(db, staleness_threshold_sessions=5)
        ids = [f["spec_id"] for f in report.findings]
        assert "SPEC-AGED" not in ids

    # 24 — insufficient-snapshot smoke: fewer than N → fallback triggers
    def test_stale_insufficient_snapshots_uses_fallback(self, db):
        """With fewer than N post-change snapshots, the snapshot path
        yields to the fallback path (no false-positive from the short
        snapshot chain)."""
        now = datetime.now(UTC)
        _insert_spec(db, "SPEC-SHORT", section="short")
        _set_spec_changed_at(db, "SPEC-SHORT", _iso(now - timedelta(days=120)))
        # Only 2 snapshots — N=5 required for the snapshot path.
        _insert_snapshot(db, "S1", _iso(now - timedelta(days=40)))
        _insert_snapshot(db, "S2", _iso(now - timedelta(days=20)))

        _insert_spec(db, "SPEC-SHORT-FRESH", section="short")
        _set_spec_changed_at(db, "SPEC-SHORT-FRESH", _iso(now - timedelta(days=3)))

        report = find_stale_specs(db, staleness_threshold_sessions=5)
        aged = [f for f in report.findings if f["spec_id"] == "SPEC-SHORT"]
        assert len(aged) == 1
        assert aged[0]["reason"] == "changed_at_fallback"


# ===========================================================================
# Section 5: Provenance (3 tests)
# ===========================================================================


class TestProvenance:
    """Expired-provisional reconciliation + duplicate-title detection."""

    # 25 — positive: replacement at status='implemented'
    def test_expired_provisional_with_implemented_replacement_reported(self, db):
        db.insert_spec(
            id="SPEC-P",
            title="Provisional",
            status="specified",  # lifecycle: NOT yet implemented
            authority="provisional",  # source: provisional
            provisional_until="SPEC-R",  # reference to replacement
            changed_by="test",
            change_reason="test seed",
        )
        db.insert_spec(
            id="SPEC-R",
            title="Replacement",
            status="implemented",  # lifecycle: shipped
            authority="stated",
            changed_by="test",
            change_reason="test seed",
        )
        report = find_expired_provisionals(db)
        assert any(f["spec_id"] == "SPEC-P" for f in report.findings)
        assert any(f["spec_id"] == "SPEC-P" and f["replacement_status"] == "implemented" for f in report.findings)

    # 26 — NEW negative discriminator: replacement still at 'specified'
    def test_provisional_with_specified_replacement_NOT_reported(self, db):
        db.insert_spec(
            id="SPEC-P",
            title="Provisional",
            status="specified",
            authority="provisional",
            provisional_until="SPEC-R",
            changed_by="test",
            change_reason="test seed",
        )
        db.insert_spec(
            id="SPEC-R",
            title="Replacement",
            status="specified",  # lifecycle: NOT yet implemented → no expiration
            authority="stated",
            changed_by="test",
            change_reason="test seed",
        )
        report = find_expired_provisionals(db)
        assert not any(f["spec_id"] == "SPEC-P" for f in report.findings)

    # 27 — duplicate spec detection (>=90% title token overlap)
    def test_duplicate_specs_90pct_title_overlap_reported(self, db):
        _insert_spec(
            db,
            "SPEC-D1",
            title="User authentication flow with password reset",
        )
        _insert_spec(
            db,
            "SPEC-D2",
            title="User authentication flow with password reset",
        )
        _insert_spec(
            db,
            "SPEC-OTHER",
            title="Completely unrelated admin panel settings",
        )
        report = find_duplicate_specs(db)
        pairs = {(f["spec_a"], f["spec_b"]) for f in report.findings}
        assert ("SPEC-D1", "SPEC-D2") in pairs
        # Unrelated spec must not appear in any pair.
        flat = {s for pair in pairs for s in pair}
        assert "SPEC-OTHER" not in flat


# ---------------------------------------------------------------------------
# CLI smoke tests (gt kb reconcile wiring)
# ---------------------------------------------------------------------------


class TestReconcileCLI:
    """Smoke tests for the ``gt kb reconcile`` CLI wiring (F8 Phase 4).

    These aren't counted toward the 27 detector-level tests from the
    proposal — they exist to prove the click command successfully
    dispatches to every detector and produces a non-zero exit-code-free
    run on a fresh KB. The subagent that wrote the detector suite did
    not have permission to modify cli.py, so the CLI wiring test is
    added here after the CLI landed.
    """

    def test_gt_kb_reconcile_all_runs_every_detector(self, tmp_path: Path, monkeypatch):
        """`gt kb reconcile --all` exits 0 on an empty KB and names every
        detector category in its output."""
        from click.testing import CliRunner

        from groundtruth_kb.cli import main

        db_path = tmp_path / "reconcile_smoke.db"
        KnowledgeDB(db_path=db_path).close()  # create empty KB

        # Create a minimal config file so _resolve_config can find the DB.
        config_path = tmp_path / "groundtruth.toml"
        config_path.write_text(
            f'[core]\ndb_path = "{db_path.as_posix()}"\n',
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--config",
                str(config_path),
                "kb",
                "reconcile",
                "--all",
                "--project-root",
                str(tmp_path),
            ],
        )
        # Exit 0, each detector category named in output, and the total-line
        # exists. Finding counts are not asserted here — a fresh KB auto-seeds
        # governance specs whose assertions point to files that don't exist in
        # tmp_path, so orphan findings > 0 is expected and correct.
        assert result.exit_code == 0, f"stdout={result.output}\n\nexc={result.exception}"
        output = result.output
        assert "[orphaned_assertions]" in output
        assert "[stale_specs]" in output
        assert "[authority_conflicts]" in output
        assert "[duplicate_specs]" in output
        assert "[expired_provisionals]" in output
        assert "Total findings across 5 detector(s):" in output
