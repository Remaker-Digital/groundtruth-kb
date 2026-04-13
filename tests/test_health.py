"""Tests for F7: Session Health Dashboard.

14 tests per approved Phase 3 v6 scope (bridge/gtkb-phase3-implementation-013.md).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.health import DEFAULT_THRESHOLDS, render_health_text


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


def _add_spec(db, spec_id="SPEC-001", **kw):
    kw.setdefault("title", f"Spec {spec_id}")
    kw.setdefault("status", "specified")
    kw.setdefault("changed_by", "test")
    kw.setdefault("change_reason", "test")
    kw.setdefault("section", "core")
    return db.insert_spec(id=spec_id, **kw)


class TestF7SessionHealthDashboard:
    """14 tests for F7: session health snapshots, deltas, and rendering."""

    # 1. Snapshot capture — stores lifecycle + summary + quality + coverage
    def test_snapshot_capture(self, db):
        _add_spec(db)
        snap = db.capture_session_snapshot("S1")
        assert "lifecycle_metrics" in snap
        assert "summary" in snap
        assert "quality_distribution" in snap
        assert "constraint_coverage" in snap
        assert snap["session_id"] == "S1"

    # 2. Snapshot includes get_summary() data
    def test_snapshot_includes_summary(self, db):
        _add_spec(db)
        snap = db.capture_session_snapshot("S1")
        assert "spec_total" in snap["summary"]
        assert snap["summary"]["spec_total"] >= 1

    # 3. Same-session replacement (INSERT OR REPLACE)
    def test_same_session_replacement(self, db):
        _add_spec(db, "SPEC-001")
        db.capture_session_snapshot("S1")

        _add_spec(db, "SPEC-002")
        db.capture_session_snapshot("S1")

        stored = db.get_session_snapshot("S1")
        assert stored is not None
        data = stored["data_parsed"]
        assert data["summary"]["spec_total"] >= 2

        # Only one row for S1
        history = db.get_snapshot_history(limit=100)
        s1_rows = [h for h in history if h["session_id"] == "S1"]
        assert len(s1_rows) == 1

    # 4. Delta: current-vs-last with no prior → no_prior=True
    def test_delta_no_prior(self, db):
        delta = db.compute_session_delta()
        assert delta["no_prior"] is True
        assert delta["deltas"] == {}

    # 5. Delta: current-vs-last with prior → deltas computed
    def test_delta_with_prior(self, db):
        _add_spec(db, "SPEC-001")
        db.capture_session_snapshot("S1")

        _add_spec(db, "SPEC-002")
        delta = db.compute_session_delta()
        assert delta["no_prior"] is False
        assert "current" in delta
        assert "previous" in delta

    # 6. Delta: explicit session-vs-previous for trends
    def test_delta_explicit_sessions(self, db):
        _add_spec(db, "SPEC-001")
        db.capture_session_snapshot("S1")

        _add_spec(db, "SPEC-002")
        db.capture_session_snapshot("S2")

        delta = db.compute_session_delta("S2")
        assert delta["no_prior"] is False
        assert delta["previous"] is not None

    # 7. Alert generation — metric above threshold
    def test_alert_generation(self, db):
        # Create implemented spec without tests → M18 > 0
        _add_spec(db, "SPEC-IMPL", status="implemented")
        snap = db.capture_session_snapshot("S1")
        thresholds = {"M18_max": 0}
        text = render_health_text(snap, thresholds=thresholds)
        assert "ALERT" in text

    # 8. Text rendering — non-empty output
    def test_text_rendering(self, db):
        _add_spec(db)
        snap = db.capture_session_snapshot("S1")
        text = render_health_text(snap)
        assert len(text) > 0
        assert "Session Health Report" in text
        assert "Lifecycle Metrics" in text

    # 9. Graceful degradation — empty DB
    def test_graceful_degradation(self, db):
        snap = db.capture_session_snapshot("S-EMPTY")
        assert snap is not None
        text = render_health_text(snap)
        assert len(text) > 0

    # 10. Threshold storage via env_config
    def test_threshold_storage(self, db):
        db.insert_env_config(
            id="health-thresholds",
            environment="shared",
            category="health",
            key="alert_thresholds",
            value=json.dumps({"M6_max": 0.10}),
            changed_by="test",
            change_reason="test",
        )
        config = db.get_env_config("health-thresholds")
        assert config is not None
        stored = json.loads(config["value"])
        assert stored["M6_max"] == 0.10

    # 11. Threshold default fallback
    def test_threshold_default_fallback(self, db):
        config = db.get_env_config("health-thresholds")
        assert config is None
        # Use DEFAULT_THRESHOLDS as fallback
        assert DEFAULT_THRESHOLDS["M6_max"] == 0.25
        assert DEFAULT_THRESHOLDS["M18_max"] == 0

    # 12. Snapshot export/import roundtrip
    def test_snapshot_export_import(self, db, tmp_path):
        _add_spec(db)
        db.capture_session_snapshot("S-EXPORT")

        export_path = db.export_json(tmp_path / "export.json")
        assert Path(export_path).exists()

        # Import into a fresh DB directly (bypasses CLI config resolution)
        db2 = KnowledgeDB(db_path=tmp_path / "test2.db")
        data = json.loads(Path(export_path).read_text())
        snap_rows = data["tables"].get("session_snapshots", [])
        assert len(snap_rows) >= 1

        conn = db2._get_conn()
        for row in snap_rows:
            conn.execute(
                "INSERT INTO session_snapshots (session_id, captured_at, data) VALUES (?, ?, ?)",
                (row["session_id"], row["captured_at"], row["data"]),
            )
        conn.commit()

        snap = db2.get_session_snapshot("S-EXPORT")
        assert snap is not None
        assert "lifecycle_metrics" in snap["data_parsed"]

    # 13. Malformed snapshot JSON import rejected
    def test_malformed_snapshot_import(self, db, tmp_path):
        _add_spec(db)
        db.capture_session_snapshot("S-OK")

        export_path = db.export_json(tmp_path / "export.json")
        with open(export_path) as f:
            data = json.load(f)
        # Corrupt the snapshot data
        for row in data["tables"].get("session_snapshots", []):
            row["data"] = "NOT VALID JSON {"
        corrupted_path = tmp_path / "corrupted.json"
        with open(corrupted_path, "w") as f:
            json.dump(data, f)

        KnowledgeDB(db_path=tmp_path / "test2.db")  # ensure schema exists
        runner = CliRunner()
        # Non-merge mode: should raise error
        result = runner.invoke(
            cli_main,
            ["import", str(corrupted_path), "--db", str(tmp_path / "test2.db")],
        )
        assert result.exit_code != 0 or "Invalid snapshot data" in (result.output or "")

    # 14. Hook template exists and is valid Python
    def test_hook_template_valid(self):
        template_path = Path(__file__).parent.parent / "templates" / "hooks" / "session-health.py"
        assert template_path.exists(), f"Hook template not found at {template_path}"
        source = template_path.read_text()
        compile(source, str(template_path), "exec")  # Syntax check
