from __future__ import annotations

import sqlite3
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.doctor import (
    _check_tafe_flow_definitions,
    _check_tafe_schema,
    run_doctor,
)
from groundtruth_kb.typed_artifact_flow import (
    FlowDefinitionService,
    canonical_reviewed_task_flow_definitions,
)


def _seeded_tafe_db(root: Path) -> KnowledgeDB:
    db = KnowledgeDB(root / "groundtruth.db")
    service = FlowDefinitionService(db)
    service.seed_reviewed_task_flow_definitions(changed_by="test", change_reason="seed test definitions")
    return db


def _definition_count(root: Path) -> int:
    conn = sqlite3.connect(root / "groundtruth.db")
    try:
        return int(conn.execute("SELECT COUNT(*) FROM flow_definitions").fetchone()[0])
    finally:
        conn.close()


def _canonical_by_id(flow_id: str) -> dict:
    return {seed["id"]: seed for seed in canonical_reviewed_task_flow_definitions()}[flow_id]


def test_tafe_doctor_checks_pass_for_seeded_phase0_db(tmp_path: Path) -> None:
    db = _seeded_tafe_db(tmp_path)
    try:
        before = _definition_count(tmp_path)

        schema = _check_tafe_schema(tmp_path)
        definitions = _check_tafe_flow_definitions(tmp_path)

        assert schema.status == "pass"
        assert definitions.status == "pass"
        assert "5 canonical definitions" in definitions.message
        assert _definition_count(tmp_path) == before
    finally:
        db.close()


def test_tafe_doctor_checks_warn_when_db_missing(tmp_path: Path) -> None:
    schema = _check_tafe_schema(tmp_path)
    definitions = _check_tafe_flow_definitions(tmp_path)

    assert schema.status == "warning"
    assert definitions.status == "warning"
    assert schema.found is False
    assert definitions.found is False


def test_tafe_schema_check_warns_when_tables_missing(tmp_path: Path) -> None:
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.execute("CREATE TABLE specifications (id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

    result = _check_tafe_schema(tmp_path)

    assert result.status == "warning"
    assert "missing tables" in result.message
    assert "flow_definitions" in result.message


def test_tafe_flow_definition_check_warns_when_seed_records_missing(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        result = _check_tafe_flow_definitions(tmp_path)
    finally:
        db.close()

    assert result.status == "warning"
    assert "missing active canonical definitions" in result.message
    assert "implementation" in result.message


def test_tafe_flow_definition_check_warns_on_required_role_drift(tmp_path: Path) -> None:
    db = _seeded_tafe_db(tmp_path)
    service = FlowDefinitionService(db)
    try:
        operation = _canonical_by_id("operation")
        drifted_roles = dict(operation["required_roles_by_stage"])
        drifted_roles["execute"] = "owner"
        service.define(
            id=operation["id"],
            flow_type=operation["flow_type"],
            title=operation["title"],
            description=operation["description"],
            stage_sequence=operation["stage_sequence"],
            required_roles_by_stage=drifted_roles,
            auq_gate_positions=operation["auq_gate_positions"],
            never_self_review_stages=operation["never_self_review_stages"],
            deterministic_carve_outs=operation["deterministic_carve_outs"],
            workspace_isolation=operation["workspace_isolation"],
            source_spec_ids=operation["source_spec_ids"],
            changed_by="test",
            change_reason="simulate required-role drift",
        )

        result = _check_tafe_flow_definitions(tmp_path)
    finally:
        db.close()

    assert result.status == "warning"
    assert "operation required_roles_by_stage drift" in result.message


def test_run_doctor_includes_tafe_checks_for_bridge_profile(tmp_path: Path) -> None:
    (tmp_path / "groundtruth.toml").write_text(
        "[groundtruth]\ndb_path = 'groundtruth.db'\n[project]\nname = 'test'\nprofile = 'dual-agent'\n",
        encoding="utf-8",
    )
    db = _seeded_tafe_db(tmp_path)
    try:
        report = run_doctor(tmp_path, "dual-agent")
    finally:
        db.close()

    checks = {check.name: check for check in report.checks}
    assert checks["TAFE schema health"].status == "pass"
    assert checks["TAFE flow definitions health"].status == "pass"
