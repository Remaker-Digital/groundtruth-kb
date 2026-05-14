"""Tests for scripts/assertion_categorize.py (Slice 3 IP-1 / IP-4).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md``
(Codex GO at -008) and ``SPEC-1662 (GOV-18: Assertion Quality Standard)``.

Uses fixture databases constructed in-memory so tests are deterministic
and independent of the live ``groundtruth.db``.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "assertion_categorize.py"


@pytest.fixture(scope="module")
def categorize_module():
    """Load assertion_categorize.py as a module without executing main()."""
    spec = importlib.util.spec_from_file_location("assertion_categorize", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_fixture_db(tmp_path: Path, runs_by_spec: dict[str, list[dict[str, Any]]]) -> Path:
    """Construct a fixture groundtruth.db with assertion_runs and specifications.

    runs_by_spec: {spec_id: [{run_at, overall_passed, results: [{description, passed, ...}]}]}
    """
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE assertion_runs (
            rowid INTEGER PRIMARY KEY,
            spec_id TEXT,
            spec_version INTEGER,
            run_at TEXT,
            overall_passed INTEGER,
            results TEXT,
            triggered_by TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE specifications (
            id TEXT,
            version INTEGER,
            status TEXT,
            title TEXT,
            PRIMARY KEY (id, version)
        )
    """)
    conn.execute("""
        CREATE VIEW current_specifications AS
        SELECT id, MAX(version) AS version, status, title
        FROM specifications GROUP BY id
    """)
    # Note: the view above doesn't pick the status from the max-version row;
    # for fixtures we always insert a single version so it's deterministic.

    for spec_id, runs in runs_by_spec.items():
        # Insert a specification row with status from the last spec entry
        # (tests override status via the spec_status fixture key).
        status = (runs[0].get("_spec_status") if runs else None) or "specified"
        conn.execute(
            "INSERT INTO specifications (id, version, status, title) VALUES (?, ?, ?, ?)",
            (spec_id, 1, status, f"fixture spec {spec_id}"),
        )
        for run in runs:
            conn.execute(
                "INSERT INTO assertion_runs (spec_id, spec_version, run_at, overall_passed, results, triggered_by) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    spec_id,
                    1,
                    run["run_at"],
                    1 if run["overall_passed"] else 0,
                    json.dumps(run["results"]),
                    "test",
                ),
            )

    conn.commit()
    conn.close()
    return db_path


def _make_run(run_at: str, results: list[dict[str, Any]], spec_status: str = "specified") -> dict[str, Any]:
    overall = all(r.get("passed", False) for r in results)
    return {
        "run_at": run_at,
        "overall_passed": overall,
        "results": results,
        "_spec_status": spec_status,
    }


def _make_result(description: str, passed: bool) -> dict[str, Any]:
    return {"type": "grep", "description": description, "passed": passed, "detail": ""}


def _recent_iso(days_ago: int = 0) -> str:
    """ISO timestamp N days before now (UTC)."""
    return (dt.datetime.now(dt.UTC) - dt.timedelta(days=days_ago)).isoformat(timespec="seconds")


def test_genuine_drift_detected(tmp_path, categorize_module):
    """Latest FAIL after 4 prior PASS within 7 days -> genuine_drift."""
    runs = [
        _make_run(_recent_iso(20), [_make_result("X", True)], spec_status="implemented"),
        _make_run(_recent_iso(15), [_make_result("X", True)], spec_status="implemented"),
        _make_run(_recent_iso(10), [_make_result("X", True)], spec_status="implemented"),
        _make_run(_recent_iso(5), [_make_result("X", True)], spec_status="implemented"),
        _make_run(_recent_iso(1), [_make_result("X", False)], spec_status="implemented"),
    ]
    _build_fixture_db(tmp_path,{"SPEC-DRIFT-1": runs})
    project_root = tmp_path

    result = categorize_module.categorize_all(
        project_root=project_root,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    counts = result["summary"]["counts_by_category"]
    assert counts["genuine_drift"] == 1, f"Expected 1 drift, got counts={counts}"
    assert counts["chronic_noise"] == 0
    assert counts["flaky"] == 0


def test_chronic_noise_detected(tmp_path, categorize_module):
    """5 consecutive FAIL for implemented spec -> chronic_noise."""
    runs = [
        _make_run(_recent_iso(d), [_make_result("X", False)], spec_status="implemented")
        for d in (20, 15, 10, 5, 1)
    ]
    _build_fixture_db(tmp_path,{"SPEC-CHRONIC-1": runs})
    result = categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    counts = result["summary"]["counts_by_category"]
    assert counts["chronic_noise"] == 1, f"Expected 1 chronic, got counts={counts}"


def test_flaky_detected(tmp_path, categorize_module):
    """Alternating PASS/FAIL in 5-run window -> flaky."""
    runs = [
        _make_run(_recent_iso(20), [_make_result("X", True)], spec_status="implemented"),
        _make_run(_recent_iso(15), [_make_result("X", False)], spec_status="implemented"),
        _make_run(_recent_iso(10), [_make_result("X", True)], spec_status="implemented"),
        _make_run(_recent_iso(5), [_make_result("X", False)], spec_status="implemented"),
        _make_run(_recent_iso(1), [_make_result("X", False)], spec_status="implemented"),
    ]
    _build_fixture_db(tmp_path,{"SPEC-FLAKY-1": runs})
    result = categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    counts = result["summary"]["counts_by_category"]
    # The latest FAIL with mixed history should classify as flaky (not chronic, not drift)
    assert counts["flaky"] == 1, f"Expected 1 flaky, got counts={counts}"
    assert counts["chronic_noise"] == 0
    assert counts["genuine_drift"] == 0


def test_healthy_stable_pass(tmp_path, categorize_module):
    """5 consecutive PASS -> healthy."""
    runs = [
        _make_run(_recent_iso(d), [_make_result("X", True)], spec_status="implemented")
        for d in (20, 15, 10, 5, 1)
    ]
    _build_fixture_db(tmp_path,{"SPEC-HEALTHY-1": runs})
    result = categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    counts = result["summary"]["counts_by_category"]
    assert counts["healthy"] == 1
    assert counts["chronic_noise"] == 0


def test_healthy_specified_status_expected_fail(tmp_path, categorize_module):
    """5 consecutive FAIL for specified-status spec -> healthy (expected)."""
    runs = [
        _make_run(_recent_iso(d), [_make_result("X", False)], spec_status="specified")
        for d in (20, 15, 10, 5, 1)
    ]
    _build_fixture_db(tmp_path,{"SPEC-EXPECTED-FAIL-1": runs})
    result = categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    counts = result["summary"]["counts_by_category"]
    # specified-status FAIL is expected; should be healthy not chronic
    assert counts["healthy"] == 1, f"Expected 1 healthy, got counts={counts}"
    assert counts["chronic_noise"] == 0


def test_categorization_deterministic(tmp_path, categorize_module):
    """Same input must produce same output."""
    runs = [
        _make_run(_recent_iso(d), [_make_result("X", d % 2 == 0)], spec_status="implemented")
        for d in (20, 15, 10, 5, 1)
    ]
    _build_fixture_db(tmp_path,{"SPEC-DET-1": runs})

    r1 = categorize_module.categorize_all(
        project_root=tmp_path, output_dir=tmp_path / "out1", dry_run=True
    )
    r2 = categorize_module.categorize_all(
        project_root=tmp_path, output_dir=tmp_path / "out2", dry_run=True
    )

    # Categories and confidences must match across runs
    assert r1["summary"]["counts_by_category"] == r2["summary"]["counts_by_category"]
    for aid, record in r1["results"].items():
        assert aid in r2["results"]
        assert record["category"] == r2["results"][aid]["category"]
        assert record["rationale"] == r2["results"][aid]["rationale"]


def test_categorization_handles_insufficient_history(tmp_path, categorize_module):
    """Assertion with <chronic threshold runs returns uncategorized when latest FAIL.

    With only 2 runs of history and a latest FAIL that doesn't have 2+ prior
    PASS runs, the result is uncategorized (insufficient data to call drift
    or chronic).
    """
    runs = [
        _make_run(_recent_iso(5), [_make_result("X", False)], spec_status="implemented"),
        _make_run(_recent_iso(1), [_make_result("X", False)], spec_status="implemented"),
    ]
    _build_fixture_db(tmp_path,{"SPEC-SHORT-1": runs})
    result = categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    counts = result["summary"]["counts_by_category"]
    # 2-run history of FAIL doesn't meet chronic threshold (5); should be uncategorized
    assert counts["uncategorized"] == 1, f"Expected 1 uncategorized, got counts={counts}"
    assert counts["chronic_noise"] == 0


def test_categorization_writes_output(tmp_path, categorize_module):
    """Non-dry-run mode writes JSON and markdown files."""
    runs = [
        _make_run(_recent_iso(d), [_make_result("X", False)], spec_status="implemented")
        for d in (20, 15, 10, 5, 1)
    ]
    _build_fixture_db(tmp_path,{"SPEC-OUT-1": runs})
    output_dir = tmp_path / "triage"

    result = categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=output_dir,
        dry_run=False,
    )

    assert (output_dir / "categories").is_dir()
    json_files = list((output_dir / "categories").glob("*.json"))
    assert len(json_files) >= 1, "Expected at least one per-assertion JSON file"

    # Summary markdown should exist under run_id directory
    run_id = result["summary"]["run_id"]
    summary_md = output_dir / run_id / "summary.md"
    summary_json = output_dir / run_id / "summary.json"
    assert summary_md.is_file(), f"Expected {summary_md} to exist"
    assert summary_json.is_file(), f"Expected {summary_json} to exist"

    # The summary should reflect the chronic categorization
    parsed = json.loads(summary_json.read_text())
    assert parsed["counts_by_category"]["chronic_noise"] == 1


def test_dry_run_does_not_mutate(tmp_path, categorize_module):
    """Dry-run mode must not write any files."""
    runs = [_make_run(_recent_iso(1), [_make_result("X", False)], spec_status="implemented")]
    _build_fixture_db(tmp_path,{"SPEC-DRY-1": runs})
    output_dir = tmp_path / "triage_dry"

    categorize_module.categorize_all(
        project_root=tmp_path,
        output_dir=output_dir,
        dry_run=True,
    )

    assert not output_dir.exists() or not list(output_dir.iterdir()), (
        f"dry-run should not create output files in {output_dir}"
    )


def test_assertion_id_includes_description_hash(tmp_path, categorize_module):
    """assertion_id should differentiate assertions with same index but different descriptions."""
    aid_a = categorize_module._assertion_id("SPEC-1", 0, "description A")
    aid_b = categorize_module._assertion_id("SPEC-1", 0, "description B")
    aid_a_dup = categorize_module._assertion_id("SPEC-1", 0, "description A")
    assert aid_a != aid_b, "Different descriptions should produce different assertion_ids"
    assert aid_a == aid_a_dup, "Same inputs must produce same assertion_id (determinism)"
