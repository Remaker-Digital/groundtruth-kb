"""Tests for discoverability CLI surfaces."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import doctor as doctor_mod


def _doctor_report(status: str = "pass") -> doctor_mod.DoctorReport:
    check = doctor_mod.ToolCheck(
        name="sample",
        required=True,
        found=status != "fail",
        status=status,
        message="sample check",
    )
    return doctor_mod.DoctorReport(checks=[check], profile="local-only")


def _seed_work_item(project_dir: Path) -> dict[str, object]:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_work_item(
            "WI-TEST-0001",
            "Initial title",
            "new",
            "backlog",
            "open",
            "tester",
            "Initial seed",
            description="Detailed work item description.",
            priority="P2",
            stage="created",
            project_name="PROJECT-TEST",
            subproject_name="PROJECT-TEST-DISCOVERABILITY",
            implementation_order=7,
            status_detail="ready",
            source_spec_id="SPEC-TEST",
            acceptance_summary="Acceptance summary text.",
        )
        return db.insert_work_item(
            "WI-TEST-0001",
            "Updated title",
            "new",
            "backlog",
            "open",
            "tester",
            "Second version",
            description="Updated work item description.",
            priority="P1",
            stage="created",
            project_name="PROJECT-TEST",
            subproject_name="PROJECT-TEST-DISCOVERABILITY",
            implementation_order=7,
            status_detail="ready",
            source_spec_id="SPEC-TEST",
            acceptance_summary="Updated acceptance summary.",
        )
    finally:
        db.close()


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def test_doctor_json_flag_emits_schema_v1_envelope(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(doctor_mod, "run_doctor", lambda *_args, **_kwargs: _doctor_report())

    result = runner.invoke(main, ["project", "doctor", "--dir", str(tmp_path), "--profile", "local-only", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["schema_version"] == "1"
    assert payload["profile"] == "local-only"
    assert payload["overall"] == "pass"


def test_doctor_json_flag_includes_all_checks(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(doctor_mod, "run_doctor", lambda *_args, **_kwargs: _doctor_report())

    result = runner.invoke(main, ["project", "doctor", "--dir", str(tmp_path), "--profile", "local-only", "--json"])

    payload = json.loads(result.output)
    assert len(payload["checks"]) == 2
    assert payload["checks"][0]["name"] == "sample"
    assert payload["checks"][0]["required"] is True
    assert payload["checks"][1]["name"] == "isolation:application-registry"


def test_doctor_json_exits_nonzero_when_overall_fail(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(doctor_mod, "run_doctor", lambda *_args, **_kwargs: _doctor_report("fail"))

    result = runner.invoke(main, ["project", "doctor", "--dir", str(tmp_path), "--profile", "local-only", "--json"])

    assert result.exit_code == 1
    assert json.loads(result.output)["overall"] == "fail"


def test_doctor_without_json_preserves_human_output(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _doctor_report()
    monkeypatch.setattr(doctor_mod, "run_doctor", lambda *_args, **_kwargs: report)

    result = runner.invoke(main, ["project", "doctor", "--dir", str(tmp_path), "--profile", "local-only"])

    assert result.exit_code == 0
    assert result.output == doctor_mod.format_doctor_report(report) + "\n"


def test_backlog_show_emits_work_item_record(runner: CliRunner, project_dir: Path) -> None:
    _seed_work_item(project_dir)

    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "show", "WI-TEST-0001"])

    assert result.exit_code == 0
    assert "ID: WI-TEST-0001" in result.output
    assert "Title: Updated title" in result.output
    assert "Priority: P1" in result.output
    assert "Acceptance Summary:" in result.output
    assert "Updated acceptance summary." in result.output


def test_backlog_show_json_flag_emits_dict(runner: CliRunner, project_dir: Path) -> None:
    expected = _seed_work_item(project_dir)

    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "show", "WI-TEST-0001", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["id"] == expected["id"]
    assert payload["version"] == expected["version"]
    assert payload["title"] == expected["title"]


def test_backlog_show_with_history_includes_version_chain(runner: CliRunner, project_dir: Path) -> None:
    _seed_work_item(project_dir)

    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "show", "WI-TEST-0001", "--history"])

    assert result.exit_code == 0
    assert "Version History:" in result.output
    assert "v2" in result.output
    assert "Second version" in result.output
    assert "v1" in result.output
    assert "Initial seed" in result.output


def test_backlog_show_missing_id_raises_clickexception(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "show", "WI-MISSING"])

    assert result.exit_code == 1
    assert "Work item not found: WI-MISSING" in result.output


def test_backlog_show_unknown_id_exits_nonzero(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "show", "WI-9999", "--json"])

    assert result.exit_code != 0
    assert "Work item not found: WI-9999" in result.output


def test_backlog_show_json_with_history_emits_current_and_history_keys(
    runner: CliRunner,
    project_dir: Path,
) -> None:
    _seed_work_item(project_dir)

    result = runner.invoke(
        main,
        [*_config_args(project_dir), "backlog", "show", "WI-TEST-0001", "--json", "--history"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert sorted(payload.keys()) == ["current", "history"]
    assert payload["current"]["id"] == "WI-TEST-0001"
    assert [row["version"] for row in payload["history"]] == [2, 1]
