"""Tests for gt backlog list-phases command (GFR Slice C Finding 1.4).

Work item: WI-5645 (TEST-11690).
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import backlog


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
        """
    )
    conn.executemany(
        "INSERT INTO test_plan_phases (id, title, last_result) VALUES (?, ?, ?)",
        [("PHASE-001", "Initial", "active"), ("PHASE-002", "Integration", "active")],
    )
    conn.commit()
    conn.close()
    return db_path


class TestListPhases:
    """Finding 1.4: gt backlog list-phases should list all test-plan phases."""

    def test_list_phases_text(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        db_path = _make_db(tmp_path)
        monkeypatch.setattr("groundtruth_kb.cli._resolve_config", lambda ctx: type("C", (), {"db_path": db_path})())
        runner = CliRunner()
        result = runner.invoke(backlog, ["list-phases"])
        assert result.exit_code == 0
        assert "PHASE-001" in result.output
        assert "PHASE-002" in result.output

    def test_list_phases_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        db_path = _make_db(tmp_path)
        monkeypatch.setattr("groundtruth_kb.cli._resolve_config", lambda ctx: type("C", (), {"db_path": db_path})())
        runner = CliRunner()
        result = runner.invoke(backlog, ["list-phases", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        assert data[0]["phase_id"] == "PHASE-001"
        assert data[1]["phase_id"] == "PHASE-002"
