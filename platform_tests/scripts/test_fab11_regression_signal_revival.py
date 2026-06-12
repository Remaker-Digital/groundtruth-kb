from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from scripts import (  # noqa: E402
    fab11_assertion_corpus_remediation as assertion_fix,
    fab11_pipeline_events_retention as retention,
    fab11_pytest_evidence_contract as pytest_contract,
)


def _db(tmp_path: Path) -> tuple[Path, KnowledgeDB]:
    db_path = tmp_path / "groundtruth.db"
    return db_path, KnowledgeDB(db_path=db_path)


def test_assertion_corpus_rewrites_critical_and_retires_history(tmp_path: Path) -> None:
    db_path, db = _db(tmp_path)
    try:
        (tmp_path / "applications" / "Agent_Red" / "src").mkdir(parents=True)
        (tmp_path / "applications" / "Agent_Red" / "src" / "app.py").write_text("hello\n", encoding="utf-8")

        db.insert_spec(
            "SPEC-CRIT",
            "Critical spec",
            "verified",
            "test",
            "seed",
            assertions=[{"type": "grep", "file": "src/app.py", "pattern": "hello"}],
        )
        db.insert_assertion_run(
            "SPEC-CRIT",
            1,
            False,
            [{"type": "grep", "passed": False, "detail": "File not found: src/app.py"}],
            "test",
        )
        db.insert_spec(
            "SPEC-OLD",
            "Old app history",
            "specified",
            "test",
            "seed",
            assertions=[{"type": "file_exists", "file": "admin/old.py"}],
        )
        db.insert_assertion_run(
            "SPEC-OLD",
            1,
            False,
            [{"type": "file_exists", "passed": False, "detail": "File not found: admin/old.py"}],
            "test",
        )
    finally:
        db.close()

    result = assertion_fix.apply_actions(db_path, tmp_path)

    assert result["rewritten"] == 1
    assert result["retired"] == 1
    db = KnowledgeDB(db_path=db_path)
    try:
        critical = db.get_spec("SPEC-CRIT")
        old = db.get_spec("SPEC-OLD")
    finally:
        db.close()
    assert critical["assertions_parsed"][0]["file"] == "applications/Agent_Red/src/app.py"
    assert old["status"] == "retired"
    assert old["assertions_parsed"] == []
    assert "fab11-app-scoped-history" in old["tags_parsed"]


def test_assertion_rewrite_preserves_json_path_expression() -> None:
    rewritten, changed = assertion_fix.rewrite_assertions(
        [{"type": "json_path", "file": "src/config.json", "path": "src/not-a-file"}],
        ("src/config.json",),
    )

    assert changed == 1
    assert rewritten[0]["file"] == "applications/Agent_Red/src/config.json"
    assert rewritten[0]["path"] == "src/not-a-file"


def test_pytest_contract_scopes_historical_tests_and_writes_packets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pytest_contract, "PROJECT_ROOT", tmp_path)
    db_path, db = _db(tmp_path)
    try:
        db.insert_spec("GOV-12", "GOV 12", "specified", "test", "seed", type="governance", description="before")
        db.insert_spec("GOV-13", "GOV 13", "specified", "test", "seed", type="governance", description="before")
        db.insert_test(
            "TEST-HIST",
            "Historical test",
            "GOV-12",
            "unit",
            "passes",
            "test",
            "seed",
            test_file="tests/test_old.py",
            last_result="pass",
            last_executed_at="2026-04-01T00:00:00+00:00",
        )
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("UPDATE tests SET changed_at = '2026-04-01T00:00:00+00:00' WHERE id = 'TEST-HIST'")
            conn.execute(
                """INSERT INTO test_coverage
                   (spec_id, test_file, test_function, confidence, match_reason, created_at, created_by)
                   VALUES (
                       'GOV-13',
                       'platform_tests/test_live.py',
                       'test_live',
                       'high',
                       'fixture',
                       '2026-06-12T00:00:00+00:00',
                       'test'
                   )"""
            )
            conn.commit()
        finally:
            conn.close()
    finally:
        db.close()

    result = pytest_contract.apply(db_path, date_text="2026-06-12")

    assert result["amended_specs"] == 2
    assert result["historical_tests_applied"] == 1
    assert (tmp_path / ".groundtruth" / "formal-artifact-approvals" / "2026-06-12-fab11-gov-12-pytest-evidence.json").is_file()
    db = KnowledgeDB(db_path=db_path)
    try:
        gov12 = db.get_spec("GOV-12")
        test = db.get_test("TEST-HIST")
        kpi = db.get_kpi_spec_test_mapping()
    finally:
        db.close()
    assert "FAB-11 pytest evidence amendment" in gov12["description"]
    assert test["last_result"] == "historical_agent_red"
    assert kpi["total_specifications"] == 2
    assert kpi["mapped_specifications"] == 1


def test_pipeline_events_retention_prunes_only_old_assertion_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(retention, "PROJECT_ROOT", tmp_path)
    db_path, db = _db(tmp_path)
    try:
        conn = sqlite3.connect(db_path)
        try:
            rows = [
                ("old-assert", "assertion_run", "2026-05-01T00:00:00+00:00"),
                ("new-assert", "assertion_run", "2026-06-11T00:00:00+00:00"),
                ("old-other", "spec_transition", "2026-05-01T00:00:00+00:00"),
            ]
            conn.executemany(
                """INSERT INTO pipeline_events
                   (id, event_type, timestamp, changed_by)
                   VALUES (?, ?, ?, 'test')""",
                rows,
            )
            conn.commit()
        finally:
            conn.close()
    finally:
        db.close()

    config = tmp_path / "pipeline-events-retention.toml"
    config.write_text(
        "\n".join(
            [
                "schema_version = 1",
                'event_type = "assertion_run"',
                "retention_days = 14",
                "delete_batch_size = 2",
                "vacuum_after_delete = false",
                'snapshot_prefix = "groundtruth.db.pre-backfill-fab11-vacuum"',
            ]
        ),
        encoding="utf-8",
    )

    result = retention.apply(db_path, config, skip_vacuum=True)

    assert result["deleted"] == 1
    assert (tmp_path / result["snapshot"]).is_file()
    conn = sqlite3.connect(db_path)
    try:
        remaining = {row[0] for row in conn.execute("SELECT id FROM pipeline_events")}
    finally:
        conn.close()
    assert "old-assert" not in remaining
    assert {"new-assert", "old-other"} <= remaining
