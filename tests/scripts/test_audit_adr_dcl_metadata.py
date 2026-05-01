"""Tests for groundtruth-kb/scripts/audit_adr_dcl_metadata.py.

Per `bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30-006.md` (GO).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "groundtruth-kb" / "scripts" / "audit_adr_dcl_metadata.py"


def _load_module():
    """Load the audit script as a module for direct function-level testing."""
    spec = importlib.util.spec_from_file_location("audit_adr_dcl_metadata", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_adr_dcl_metadata"] = module
    spec.loader.exec_module(module)
    return module


def _seed_fixture_db(db_path: Path) -> None:
    """Create a minimal specifications-table fixture covering all population states."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE specifications (
            id TEXT,
            version INTEGER,
            type TEXT,
            tags TEXT,
            source_paths TEXT,
            assertions TEXT
        )
        """
    )
    rows = [
        # ADR fully populated
        ("ADR-001", 1, "architecture_decision",
         '["theme-tag", "design-constraint", "topic-foo"]',
         '["scripts/foo.py"]',
         '[{"type": "grep", "pattern": "x"}]'),
        # ADR with tags only
        ("ADR-002", 1, "architecture_decision",
         '["theme-tag", "topic-bar"]',
         "",
         "[]"),
        # ADR with no metadata
        ("ADR-003", 1, "architecture_decision", "", "", ""),
        # DCL fully populated
        ("DCL-001", 1, "design_constraint",
         '["mechanical-enforcement", "topic-foo"]',
         '["src/bar.py"]',
         '[{"type": "grep", "pattern": "y"}]'),
        # DCL with tags + assertions but no source_paths
        ("DCL-002", 1, "design_constraint",
         '["theme-tag", "design-constraint"]',
         "[]",
         '[{"type": "grep", "pattern": "z"}]'),
        # DCL with no metadata
        ("DCL-003", 1, "design_constraint", None, None, None),
    ]
    conn.executemany(
        "INSERT INTO specifications (id, version, type, tags, source_paths, assertions) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def _connect_and_query(module, db_path: Path):
    with module._connect_read_only(db_path) as conn:
        return module._query_records(conn)


def _build_report(module, db_path: Path, frozen_ts: str = "2026-05-01T00:00:00+00:00"):
    records = _connect_and_query(module, db_path)
    return module.build_report(records, db_path, frozen_ts)


# Test 1: idempotency
def test_idempotency_byte_identical_with_frozen_timestamp(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    frozen = "2026-05-01T12:00:00+00:00"

    report1 = _build_report(module, db, frozen)
    report2 = _build_report(module, db, frozen)

    assert module.render_json(report1) == module.render_json(report2)
    assert module.render_markdown(report1) == module.render_markdown(report2)


# Test 2: population computation
def test_population_computation(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    report = _build_report(module, db)

    totals = report["totals"]
    assert totals["architecture_decision"]["total"] == 3
    assert totals["architecture_decision"]["with_tags"] == 2  # ADR-001, ADR-002
    assert totals["architecture_decision"]["with_source_paths"] == 1  # ADR-001
    assert totals["architecture_decision"]["with_assertions"] == 1  # ADR-001

    assert totals["design_constraint"]["total"] == 3
    assert totals["design_constraint"]["with_tags"] == 2  # DCL-001, DCL-002
    assert totals["design_constraint"]["with_source_paths"] == 1  # DCL-001
    assert totals["design_constraint"]["with_assertions"] == 2  # DCL-001, DCL-002


# Test 3: missing source_paths list
def test_missing_source_paths_list_correct(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    report = _build_report(module, db)

    missing_ids = [entry["id"] for entry in report["missing_source_paths"]]
    assert missing_ids == sorted(missing_ids)  # sorted invariant
    assert set(missing_ids) == {"ADR-002", "ADR-003", "DCL-002", "DCL-003"}
    assert report["records_needing_backfill_count"] == 4


# Test 4a: tags histogram explicit-marker categorization
def test_histogram_explicit_marker_categorization(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    report = _build_report(module, db)

    by_tag = {entry["tag"]: entry for entry in report["tags_histogram"]}
    # Explicit markers always 'theme' regardless of count
    assert by_tag["design-constraint"]["category"] == "theme"
    assert by_tag["mechanical-enforcement"]["category"] == "theme"


# Test 4b: tags histogram count-threshold categorization
def test_histogram_count_threshold_categorization(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    report = _build_report(module, db)

    by_tag = {entry["tag"]: entry for entry in report["tags_histogram"]}
    # theme-tag appears in 3 records (ADR-001, ADR-002, DCL-002) -> theme by count
    assert by_tag["theme-tag"]["count"] == 3
    assert by_tag["theme-tag"]["category"] == "theme"
    # topic-foo appears in 2 records (ADR-001, DCL-001) -> below threshold -> topic
    assert by_tag["topic-foo"]["count"] == 2
    assert by_tag["topic-foo"]["category"] == "topic"


# Test 5: JSON snapshot
def test_json_snapshot_deterministic_and_valid(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    report = _build_report(module, db, "2026-05-01T00:00:00+00:00")

    rendered = module.render_json(report)
    parsed = json.loads(rendered)
    assert parsed["schema_version"] == 1
    assert parsed["generated_at"] == "2026-05-01T00:00:00+00:00"
    assert "totals" in parsed
    assert "missing_source_paths" in parsed
    assert "tags_histogram" in parsed
    assert "concern_tags_normalization_recommendation" in parsed


# Test 6: markdown snapshot
def test_markdown_snapshot_contains_required_sections(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    report = _build_report(module, db, "2026-05-01T00:00:00+00:00")
    rendered = module.render_markdown(report)

    assert "# ADR/DCL Metadata Audit Report" in rendered
    assert "## Totals" in rendered
    assert "## Records needing backfill" in rendered
    assert "## Tags histogram" in rendered
    assert "## concern_tags normalization recommendation" in rendered
    assert "Generated: 2026-05-01T00:00:00+00:00" in rendered


# Test 7: read-only DB safety
def test_read_only_db_access_rejects_writes(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    mtime_before = db.stat().st_mtime_ns

    # Run audit.
    with module._connect_read_only(db) as conn:
        records = module._query_records(conn)
        assert len(records) == 6
        # Attempt to INSERT through the read-only connection -> must raise.
        with pytest.raises(sqlite3.OperationalError):
            conn.execute(
                "INSERT INTO specifications (id, version, type) "
                "VALUES ('SHOULD-FAIL', 1, 'architecture_decision')"
            )

    # mtime must be unchanged after read-only access.
    assert db.stat().st_mtime_ns == mtime_before


# Test 8: --output flag
def test_output_flag_writes_file(tmp_path: Path) -> None:
    module = _load_module()
    db = tmp_path / "fixture.db"
    _seed_fixture_db(db)
    out = tmp_path / "report.json"

    rc = module.main([
        "--db", str(db),
        "--format", "json",
        "--output", str(out),
        "--frozen-timestamp", "2026-05-01T00:00:00+00:00",
    ])

    assert rc == 0
    assert out.is_file()
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["schema_version"] == 1


# Test 9: missing DB graceful error
def test_missing_db_graceful_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_module()
    bogus = tmp_path / "does-not-exist.db"

    rc = module.main(["--db", str(bogus), "--format", "json"])

    assert rc == 2
    captured = capsys.readouterr()
    assert "groundtruth.db not found" in captured.err
