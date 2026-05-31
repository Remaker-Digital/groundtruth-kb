"""Tests for ``scripts/spec_to_test_mapper.py`` (verify-skill Slice 2, WI-3261).

Per ``bridge/gtkb-verify-skill-spec-to-test-mapping-005.md`` (Codex GO at ``-006``),
the helper supports a markdown table by default and a JSON variant under
``--json``, with bridge-id extraction and explicit ``--spec-id`` input modes.

Test fixtures use a temporary SQLite database matching the live
``current_tests`` and ``assertion_runs`` schemas per the proposal's Schema
Reconciliation Note. They never read or mutate the live ``groundtruth.db``.

Linked specs under verification:
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-derived testing
  contract; this helper is the read-side surface verify skills use to extract
  spec-to-test mappings.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the spec-linkage
  contract; bridge-id extraction supports the verify-skill's reading of
  cited specification IDs from bridge content.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "spec_to_test_mapper.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("spec_to_test_mapper", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["spec_to_test_mapper"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mapper():
    return _load_module()


@pytest.fixture
def fixture_db(tmp_path: Path) -> Path:
    """Build a minimal SQLite DB matching the live schema.

    Per the proposal's Schema Reconciliation Note:
    - ``current_tests`` columns include id, spec_id, test_file, last_result,
      last_executed_at (test-path source is ``test_file``, not ``test_path``).
    - ``assertion_runs`` columns include spec_id, run_at, overall_passed (no
      ``run_id`` column exists; ``rowid`` is the optional source).
    """
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE current_tests (
            id TEXT NOT NULL,
            version INTEGER,
            title TEXT,
            spec_id TEXT,
            test_type TEXT,
            test_file TEXT,
            test_class TEXT,
            test_function TEXT,
            description TEXT,
            expected_outcome TEXT,
            last_result TEXT,
            last_executed_at TEXT,
            changed_by TEXT,
            changed_at TEXT,
            change_reason TEXT
        );
        CREATE TABLE assertion_runs (
            spec_id TEXT NOT NULL,
            spec_version INTEGER,
            run_at TEXT,
            overall_passed INTEGER,
            results TEXT,
            triggered_by TEXT
        );
        """
    )
    conn.executemany(
        "INSERT INTO current_tests (id, spec_id, test_file, last_result, last_executed_at) VALUES (?, ?, ?, ?, ?)",
        [
            ("T-001", "SPEC-1234", "tests/test_foo.py", "passed", "2026-05-29T10:00:00Z"),
            ("T-002", "SPEC-1234", "tests/test_bar.py", "failed", "2026-05-29T11:00:00Z"),
            ("T-003", "GOV-08", "tests/test_gov.py", None, None),
        ],
    )
    conn.executemany(
        "INSERT INTO assertion_runs (spec_id, run_at, overall_passed) VALUES (?, ?, ?)",
        [
            ("SPEC-1234", "2026-05-28T10:00:00Z", 1),
            ("SPEC-1234", "2026-05-29T12:00:00Z", 0),
            ("GOV-08", "2026-05-29T08:00:00Z", 1),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


def test_markdown_table_output(mapper, fixture_db, capsys):
    """Mapper emits a markdown table with the contracted column headers."""
    rc = mapper.main(["--spec-id", "SPEC-1234", "--db-path", str(fixture_db)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "| Spec | Test ID | Test Path | Test Status |" in out
    assert "SPEC-1234" in out
    assert "T-001" in out
    assert "T-002" in out
    assert "tests/test_foo.py" in out


def test_json_output_shape(mapper, fixture_db, capsys):
    """Mapper emits JSON with the contracted shape under --json."""
    rc = mapper.main(["--spec-id", "SPEC-1234", "--json", "--db-path", str(fixture_db)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert "specs" in payload
    assert len(payload["specs"]) == 1
    spec = payload["specs"][0]
    assert spec["spec_id"] == "SPEC-1234"
    assert len(spec["tests"]) == 2
    test_keys = set(spec["tests"][0].keys())
    assert {"test_id", "test_path", "last_result", "last_executed_at"} <= test_keys


def test_spec_with_no_linked_tests_reports_none(mapper, fixture_db, capsys):
    """Spec with no current_tests rows reports (none) and 'no linked tests'."""
    rc = mapper.main(["--spec-id", "SPEC-9999", "--db-path", str(fixture_db)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "(none)" in out
    assert "no linked tests" in out


def test_per_test_status_from_last_result(mapper, fixture_db, capsys):
    """Per-test status comes from current_tests.last_result, not assertion_runs."""
    rc = mapper.main(["--spec-id", "SPEC-1234", "--json", "--db-path", str(fixture_db)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    statuses = {t["test_id"]: t["last_result"] for t in payload["specs"][0]["tests"]}
    assert statuses["T-001"] == "passed"
    assert statuses["T-002"] == "failed"


def test_test_with_null_last_result_reports_not_run(mapper, fixture_db, capsys):
    """Test row with no last_result reports per-test status 'not_run'."""
    rc = mapper.main(["--spec-id", "GOV-08", "--db-path", str(fixture_db)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "not_run" in out


def test_assertion_run_separate_from_per_test_status(mapper, fixture_db, capsys):
    """Assertion-run status is separate from per-test status and does not
    overwrite it. Per-test results remain authoritative; assertion run is
    summary-only."""
    rc = mapper.main(["--spec-id", "SPEC-1234", "--json", "--db-path", str(fixture_db)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    spec = payload["specs"][0]
    statuses = {t["test_id"]: t["last_result"] for t in spec["tests"]}
    assert statuses["T-001"] == "passed"
    assert statuses["T-002"] == "failed"
    assertion = spec["latest_assertion_run"]
    assert assertion is not None
    assert assertion["overall_passed"] is False
    assert assertion["run_at"] == "2026-05-29T12:00:00Z"


def test_no_assertion_run_reports_unknown(mapper, fixture_db, capsys):
    """Spec with no assertion runs reports assertion status 'unknown'."""
    rc = mapper.main(["--spec-id", "SPEC-7777", "--db-path", str(fixture_db)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "unknown" in out


def test_bridge_extraction_from_specification_links(mapper, fixture_db, tmp_path, capsys):
    """Bridge-id extraction parses spec IDs from bridge file content."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "demo-thread-001.md").write_text(
        "NEW\n\n## Specification Links\n\n- SPEC-1234\n- GOV-08\n",
        encoding="utf-8",
    )
    rc = mapper.main(
        [
            "--bridge-id",
            "demo-thread",
            "--db-path",
            str(fixture_db),
            "--bridge-dir",
            str(bridge_dir),
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    spec_ids = {s["spec_id"] for s in payload["specs"]}
    assert "SPEC-1234" in spec_ids
    assert "GOV-08" in spec_ids


def test_bridge_extraction_picks_latest_version(mapper, fixture_db, tmp_path, capsys):
    """Bridge-id extraction selects the highest-numbered file in the thread."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "multi-version-001.md").write_text("NEW\n## Specification Links\n- SPEC-1234\n", encoding="utf-8")
    (bridge_dir / "multi-version-003.md").write_text("REVISED\n## Specification Links\n- GOV-08\n", encoding="utf-8")
    (bridge_dir / "multi-version-002.md").write_text("NO-GO\n## Specification Links\n- SPEC-9999\n", encoding="utf-8")
    rc = mapper.main(
        [
            "--bridge-id",
            "multi-version",
            "--db-path",
            str(fixture_db),
            "--bridge-dir",
            str(bridge_dir),
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    spec_ids = {s["spec_id"] for s in payload["specs"]}
    # Latest is -003 which cites GOV-08; not SPEC-1234 (-001) or SPEC-9999 (-002).
    assert "GOV-08" in spec_ids
    assert "SPEC-1234" not in spec_ids
    assert "SPEC-9999" not in spec_ids


def test_invalid_db_path_returns_nonzero(mapper, tmp_path, capsys):
    """Missing database returns non-zero exit."""
    rc = mapper.main(["--spec-id", "SPEC-1234", "--db-path", str(tmp_path / "nonexistent.db")])
    assert rc != 0


def test_missing_bridge_thread_returns_nonzero(mapper, fixture_db, tmp_path, capsys):
    """Missing bridge thread returns non-zero exit (bridge dir exists but empty)."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    rc = mapper.main(
        [
            "--bridge-id",
            "nonexistent-thread",
            "--db-path",
            str(fixture_db),
            "--bridge-dir",
            str(bridge_dir),
        ]
    )
    assert rc != 0


def test_no_input_raises_systemexit(mapper):
    """Either --bridge-id or --spec-id is required; argparse error -> SystemExit."""
    with pytest.raises(SystemExit):
        mapper.main([])


def test_spec_id_pattern_excludes_delib(mapper):
    """SPEC_ID_PATTERN must NOT match DELIB-NNNN (deliberation IDs are not specs)."""
    text = "Cites SPEC-1234, GOV-08, DELIB-2077, and DCL-FOO-001."
    matches = mapper.SPEC_ID_PATTERN.findall(text)
    assert "SPEC-1234" in matches
    assert "GOV-08" in matches
    assert "DCL-FOO-001" in matches
    assert not any("DELIB" in m for m in matches)
