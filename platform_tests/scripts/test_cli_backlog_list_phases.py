"""Tests for gt backlog list-phases command (GFR Slice C Finding 1.4).

Work item: WI-5645 (TEST-11690); WI-6315 (TEST-11948).
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001,
GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, GOV-13.

WI-6315 conversion note: the original fixture created only the append-only
``test_plan_phases`` base table and seeded one version per phase, so the base
table and the ``current_test_plan_phases`` view returned identical rows and the
tests could not distinguish the defect from the fix. The fixture now creates the
view with MemBase's own definition and seeds MULTIPLE versions per phase, so the
two diverge. The two original tests keep their names and their original
assertions, which remain true; each gains an exact row-count assertion.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import backlog

# Two phases, seeded at several versions each. A reader that returns history
# emits _TOTAL_VERSIONS rows; a reader that returns current state emits 2.
_PHASE_VERSIONS = {"PHASE-001": 4, "PHASE-002": 3}
_TOTAL_VERSIONS = sum(_PHASE_VERSIONS.values())
_DISTINCT_PHASES = len(_PHASE_VERSIONS)


def _make_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS test_plan_phases (
            rowid INTEGER PRIMARY KEY,
            id TEXT,
            version INTEGER DEFAULT 1,
            plan_id TEXT,
            phase_order INTEGER,
            title TEXT,
            description TEXT,
            gate_criteria TEXT,
            test_ids TEXT,
            last_result TEXT,
            last_executed_at TEXT,
            changed_by TEXT,
            changed_at TEXT,
            change_reason TEXT
        );
        CREATE VIEW IF NOT EXISTS current_test_plan_phases AS
        SELECT t.* FROM test_plan_phases t
        INNER JOIN (
            SELECT id, MAX(version) AS max_v FROM test_plan_phases GROUP BY id
        ) m ON t.id = m.id AND t.version = m.max_v;
        """
    )
    rows = []
    for phase_id, versions in _PHASE_VERSIONS.items():
        title = "Initial" if phase_id == "PHASE-001" else "Integration"
        for version in range(1, versions + 1):
            # Only the newest version carries the current result. Earlier
            # versions carry a different value, so a history-reading reader
            # emits statuses that were never current.
            is_current = version == versions
            rows.append((phase_id, version, title, "active" if is_current else "stale"))
    conn.executemany(
        "INSERT INTO test_plan_phases (id, version, title, last_result) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return db_path


def _patch_config(monkeypatch: pytest.MonkeyPatch, db_path: Path) -> None:
    monkeypatch.setattr(
        "groundtruth_kb.cli._resolve_config",
        lambda ctx: type("C", (), {"db_path": db_path})(),
    )


class TestListPhases:
    """Finding 1.4: gt backlog list-phases should list all test-plan phases."""

    def test_list_phases_text(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        db_path = _make_db(tmp_path)
        _patch_config(monkeypatch, db_path)
        runner = CliRunner()
        result = runner.invoke(backlog, ["list-phases"])
        assert result.exit_code == 0
        # Original assertions, still true.
        assert "PHASE-001" in result.output
        assert "PHASE-002" in result.output
        # WI-6315: one row per distinct phase, not one per version.
        lines = [line for line in result.output.splitlines() if line.strip()]
        assert len(lines) == _DISTINCT_PHASES, f"expected {_DISTINCT_PHASES} rows, got {len(lines)}"

    def test_list_phases_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        db_path = _make_db(tmp_path)
        _patch_config(monkeypatch, db_path)
        runner = CliRunner()
        result = runner.invoke(backlog, ["list-phases", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        # Original assertions, still true.
        assert data[0]["phase_id"] == "PHASE-001"
        assert data[-1]["phase_id"] == "PHASE-002"
        # WI-6315: exactly one entry per distinct phase.
        assert len(data) == _DISTINCT_PHASES, f"expected {_DISTINCT_PHASES} entries, got {len(data)}"
        assert [entry["phase_id"] for entry in data] == sorted(_PHASE_VERSIONS)


def test_row_count_does_not_grow_with_phase_versions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The emitted row count tracks phase count, never version count."""
    db_path = _make_db(tmp_path)
    _patch_config(monkeypatch, db_path)
    result = CliRunner().invoke(backlog, ["list-phases", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == _DISTINCT_PHASES
    assert len(data) != _TOTAL_VERSIONS, "reader is returning append-only history, not current state"


def test_status_reflects_the_current_phase_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reported status comes from the current version, never a superseded one."""
    db_path = _make_db(tmp_path)
    _patch_config(monkeypatch, db_path)
    result = CliRunner().invoke(backlog, ["list-phases", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert {entry["status"] for entry in data} == {"active"}, "a superseded version's status was emitted"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
